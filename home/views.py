from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from requests import Session, get
from bs4 import BeautifulSoup
from time import sleep, time
from json import dump, load, dumps
from .models import Consultant, Estate, Neighbourhood, SizeClassification
from notifypy import Notify
from shutil import get_terminal_size
from django.contrib import messages


class HomeView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home/home.html')


class SearchView(View):

    def get(self, request, *args, **kwargs):
        global time1, session, columns, loop429, number_of_requests
        session = Session()
        number_of_requests = 0
        loop429 = 0
        time1 = time()
        columns = get_terminal_size().columns

        print('  Scrapper started  '.center(columns) + '\n\n')

        res = search_in_divar()

        # try:
        #     res = search_in_divar()
        # except Exception as e:
        #     print_exc()
        #     notification = Notify()
        #     notification.title = 'Exception in divar_search'
        #     notification.message = e
        #     notification.send()
        #     sleep(100)

        process_time = int(time() - time1) // 60
        print(process_time)
        process_time = f'{process_time // 60} hours, {process_time % 60} minutes' if process_time > 60 else f'{process_time} minutes'

        print(
            f'The information of {len(res)} consultants was obtained And Saved.'.center(columns))
        print(
            f'Process Time: {process_time}'.center(columns) + '\n')

        messages.success(
            request, f'The information of {len(res)} consultants was obtained', 'info')
        messages.success(
            request, f'Process Time: {process_time}', 'info')
        messages.success(
            request, f'Go to admin panel to view results', 'success')

        return render(request, 'home/home.html')


def get_res(link):
    global columns, number_of_requests, loop429
    number_of_requests += 1
    res = session.get(link)
    columns = get_terminal_size().columns
    print(
        f' {number_of_requests} requests '.center(columns), end='\r')

    if res.status_code not in (429, 500):
        if res.status_code != 200 and res.status_code != 404:
            print('='*90)
            print(res.status_code)
            print(link)
            print('='*90 + '\n')
        loop429 = 0
        return res
    elif res.status_code == 429:
        loop429 += 1
        if loop429 >= 3:
            sleep(1)
        sleep(0.4)
        print('429 HttpError: too many requests'.center(columns), end='\r')
        return get_res(link)
    elif res.status_code == 500:
        sleep(1)
        print('\n500 HttpError: server error')
        return get_res(link)


def post_res(link, json=None):
    global number_of_requests, columns

    number_of_requests += 1
    columns = get_terminal_size().columns

    print(
        f' {number_of_requests} requests '.center(columns), end='\r')

    res = session.post(link, json=json) if json else session.post(link)

    return res


def get_ads_of_a_neighbourhood():
    data = {
        "page": 0,
        "json_schema": {
            "category": {"value": "real-estate"},
            # "districts": {"vacancies": ["907", "40", "654", "87"]},
            "districts": {
                "vacancies":
                    [
                        "40", "1024", "266", "360", "42", "43", "46", "47", "48", "52", "53", "54", "55", "56", "61", "62", "63", "64", "65", "66", "67", "68", "70", "71", "85", "931", "943"
                    ]
            },
            "sort": {"value": "sort_date"},
            "cities": ["1"]
        },
        # "last-post-date": 1691301438332056
    }
    suggestions = []
    for i in range(1):
        data['page'] = i

        res = post_res(
            'https://api.divar.ir/v8/web-search/1/real-estate', json=data)

        if res.status_code == 429:
            sleep(1)
            res = post_res(
                'https://api.divar.ir/v8/web-search/1/real-estate', json=data)
        try:
            json_res = res.json()
        except Exception as e:
            if str(e) == '[Errno Expecting value] : 0':
                print('res.text in None')
                print(res.status_code)
                continue
            print(res.text)
            print(data['page'])
            raise

        post_list = json_res['web_widgets']['post_list']
        last_post_date = json_res['last_post_date']

        for item in post_list:
            if not item['data'].get('action'):
                continue
            try:
                token = item['data']['token']
            except:
                continue
                print(item)
                print(post_list)
                with open('debug.json', 'w') as file:
                    dump({'data': post_list}, file, indent=2)
                raise

            link = 'https://divar.ir/v/' + token
            if link not in suggestions:
                suggestions.append(link)
        data['last_post_date'] = last_post_date

    suggestions = get_good_urls(suggestions)

    print(f'The Link of {len(suggestions)} ads obtained'.center(columns))

    return suggestions


def get_consultant_link_from_ads(ads):
    result = []

    for link in ads:
        res = get_res(link)

        data = BeautifulSoup(res.text, 'html.parser')
        name = data.find_all(
            'a', class_='kt-unexpandable-row__action kt-text-truncate')
        if name:
            link_of_consultant = 'https://divar.ir' + name[-1].attrs['href']
            if link_of_consultant not in result:
                result.append(link_of_consultant)

    print(f'The Link of {len(result)} consultants obtained'.center(
        columns) + '\n')
    print(f'Start to get consultants information...'.center(columns) + '\n')

    return result


def get_consultant_information(links):
    global number_of_requests
    # links = ['https://divar.ir/real-estate/agencies/agent_rPSROq3k']
    info = {}
    for link in links:
        url = 'https://api.divar.ir/v8/real-estate/w/agency-public-view'

        agent = link.split('/')[-1]
        session.options(url, headers={
                        'Access-Control-Request-Headers': 'content-type', 'Access-Control-Request-Method': 'POST'})
        number_of_requests += 1

        res = post_res(url, json={'request_data': {'slug': agent}, 'specification': {
            'tab_identifier': 'AGENT_INFO', 'filter_data': {}}})

        if not info.get(agent):
            for item in res.json()['page']['widget_list']:
                if item.get('widget_type') == 'LEGEND_TITLE_ROW':

                    if info.get(agent):
                        if not info.get(agent).get('name'):
                            name = item['data']['title']
                            info[agent] = {
                                'name': name,
                            }
                    else:
                        name = item['data']['title']
                        info[agent] = {'name': name}

                elif item.get('widget_type') == 'GROUP_INFO_ROW':
                    ads = item['data']['items'][0]['value']
                    info[agent]['number_of_ads'] = convert_number_to_english(
                        ads)

                elif item.get('widget_type') == 'UNEXPANDABLE_ROW':
                    if item['data'].get('action'):
                        info[agent]['phone_number'] = item['data']['action']['payload']['phone_number']

                elif item.get('widget_type') == 'DESCRIPTION_ROW':
                    if item['data']['text'] in ('مشاور', 'کارشناس فروش'):
                        continue
                    if not info.get(agent).get('profile'):
                        info[agent]['profile'] = item['data']['text']

                elif item.get('widget_type') == 'EVALUATION_ROW':
                    info[agent]['revenue'] = float(
                        item['data']['indicator_text'].replace('٫', '.'))

        info[agent]['link'] = link

        ads = get_ads_of_a_consultant(agent)

        info[agent]['ads'] = get_ads_information(ads)

        submit_consultant_data_to_db(agent, info[agent])

        print(
            f'{links.index(link) + 1} - {info[agent]["name"]} - obtained'.center(columns))

    return info


def get_ads_of_a_consultant(agent, last_item_identifier=None):
    global number_of_requests

    data = {
        "request_data": {"slug": agent},
        "specification": {
            "tab_identifier": "AGENT_POSTS",
            # "last_item_identifier": "1688994785064879",
            "filter_data": {}
        }
    }

    if last_item_identifier:
        data['specification']['last_item_identifier'] = last_item_identifier

    def retry():
        try:
            res = post_res(
                'https://api.divar.ir/v8/real-estate/w/agency-public-view', json=data)

            res_json = res.json()
            return res_json
        except:
            sleep(1)
            return retry()

    res_json = retry()

    try:
        widget_list = res_json['page']['widget_list']
    except:
        widget_list = []

    noa = len(widget_list)

    ads = []
    for item in widget_list:
        action = item['data'].get('action')
        if action:
            link = 'https://divar.ir/v/' + action['payload']['token']
            ads.append(link)
        else:
            print(action)

    if noa == 24:
        sub_last_item_identifier = res_json['page']['infinite_scroll_response']['last_item_identifier']
        result = get_ads_of_a_consultant(
            agent, last_item_identifier=sub_last_item_identifier)
        ads.extend(result)

    return ads


def get_ads_information(links):
    new_links = get_good_urls(links)

    result = {}
    for link in new_links:
        res = retry_request(link)

        if res == 404:
            continue

        split_link = link.split('/')
        ads_agent = split_link[-1]
        del split_link[-2]

        result[ads_agent] = {'link': '/'.join(split_link)}

        content = BeautifulSoup(res.text, 'html.parser')

        name = content.find(
            'div', class_='kt-page-title__title kt-page-title__title--responsive-sized').text

        size = content.find(
            'div', class_='kt-group-row-item kt-group-row-item--info-row')

        size = convert_number_to_english(
            size.find_all('span')[-1].text) if size else None

        if not size:
            var = content.find(
                'div', class_='kt-base-row__end kt-unexpandable-row__value-box')
            if var:
                var = var.find('p').text if var.find('p') else ''
                if 'متر' in var:
                    size = var.replace('متر', '')
                    size = convert_number_to_english(size)

        neighbourhood = content.find(
            'div', class_='kt-page-title__subtitle kt-page-title__subtitle--responsive-sized').text

        start = neighbourhood.find('،') + 2
        neighbourhood = neighbourhood[start:]
        end = neighbourhood.find('،')
        if end != -1:
            neighbourhood = neighbourhood[:end]

        result[ads_agent]['name'] = name
        result[ads_agent]['size'] = size
        result[ads_agent]['neighbourhood'] = neighbourhood

    return result


def get_good_urls(links):
    tokens = [link.split('/')[-1] for link in links]

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    chunk_token = divide_chunks(tokens, 50)
    result = []
    for tokens in chunk_token:
        if tokens:
            json_res = convert_response_to_json(tokens)
            # print(dumps(json_res))

            result.extend(json_res['widget_list'])

    new_links = []
    for item in result:
        link = item['data']['url']
        new_links.append(link)

    return new_links


def convert_response_to_json(tokens):
    global number_of_requests
    try:
        res = post_res(
            'https://api.divar.ir/v5/posts/list', json={'tokens': tokens})
        json_res = res.json()
        json_res['widget_list']
        return json_res
    except Exception:
        sleep(1)
        # print(f'we have error in get posts')
        return convert_response_to_json(tokens)


def retry_request(link):

    res = get_res(link)

    if res.status_code == 404:
        return 404

    content = BeautifulSoup(res.text, 'html.parser')

    name = content.find(
        'div', class_='kt-page-title__title kt-page-title__title--responsive-sized')

    if name:

        return res
    else:
        sleep(0.5)
        # print(f'we have error in link: {link}')

        return retry_request(link)


def submit_consultant_data_to_db(agent, info):
    consultant = Consultant.objects.get_or_create(
        agent=agent,
    )[0]

    consultant.name = info['name']
    consultant.phone_number = info.get('phone_number')
    consultant.revenue = info.get('revenue')
    consultant.profile = info.get('profile')
    consultant.number_of_ads = info.get('number_of_ads')
    consultant.link = info.get('link')
    consultant.save()
    consultant.estates.all().delete()

    if info.get('ads'):
        estates = []
        neighbourhoods = []
        for k1, v1 in info['ads'].items():
            neighbourhood = Neighbourhood.objects.get_or_create(
                title=v1['neighbourhood'])[0]

            neighbourhoods.append(neighbourhood)
            estate = Estate.objects.get_or_create(
                link=v1['link'],
            )[0]
            estate.title = v1.get('name')
            estate.size = v1.get('size')
            estate.consultant = consultant
            estate.neighbourhood = neighbourhood
            estate.save()
            estates.append(estate)

        consultant.scope_of_activity.add(*neighbourhoods)
        # consultant.scope_of_activity_string = ', '.join(
        #     [obj.title for obj in consultant.scope_of_activity.all()])
        # consultant.save()
        size_classification = SizeClassification.objects.all().order_by('id')
        obj0 = obj1 = obj2 = last = False

        for estate in estates:
            if 0 < estate.size <= 150 and not obj0:
                consultant.size_classification.add(size_classification[0])
                obj0 = True
            elif 150 < estate.size <= 250 and not obj1:
                consultant.size_classification.add(size_classification[1])
                obj1 = True
            elif 250 < estate.size <= 500 and not obj2:
                consultant.size_classification.add(size_classification[2])
                obj2 = True
            elif not last:
                max_size = Estate.objects.filter(
                    consultant=consultant).order_by('-size').first().size
                if max_size > 500:
                    title = f'500 تا {max_size} متر'
                    sc = SizeClassification.objects.get_or_create(
                        title=title)[0]
                    consultant.size_classification.add(sc)
                last = True
            if obj0 and obj1 and obj2 and last:
                break


def search_in_divar():
    global number_of_requests, Session

    number_of_requests = 0

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Origin': 'https://divar.ir',
        'Referer': 'https://divar.ir/',
    })
    session.cookies.update({'pwa-banner-closed': 'true'})

    ads = get_ads_of_a_neighbourhood()
    links = get_consultant_link_from_ads(ads)
    consultant_info = get_consultant_information(links)

    print(f"Number of requests: {number_of_requests}".center(columns) + '\n')

    return consultant_info


def convert_number_to_english(strIn: str):
    P2E_map = {'۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5',
               '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۰': '1'}

    a = map(lambda ch: P2E_map[ch] if ch in P2E_map else '', strIn)
    try:
        return int(''.join(list(a)))
    except Exception as e:
        print('Error --> ', e)
        return ''.join(list(a))
