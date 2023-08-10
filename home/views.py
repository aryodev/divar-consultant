from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from requests import Session, get
from bs4 import BeautifulSoup
from time import sleep, time
from .models import Consultant, Estate, Neighbourhood, SizeClassification, Agency, Operation
from django.contrib import messages
from requests.exceptions import ConnectTimeout, Timeout, ReadTimeout, ConnectionError, SSLError
from random import randint
from fake_useragent import UserAgent
from traceback import format_exc
from django.utils import timezone
from subprocess import run, TimeoutExpired
from json import loads
from random import randint


sc = SizeClassification.objects.filter(id__lte=3)
if sc.count() != 3:
    SizeClassification.objects.create(title='0 تا 150 متر')
    SizeClassification.objects.create(title='150 تا 250 متر')
    SizeClassification.objects.create(title='250 تا 500 متر')
else:
    pass


def Handler404(request, exception, *args, **kwargs):
    messages.warning(request, f'404 Not Found in {request.path}', 'warning')
    return redirect('home:home')


class HomeView(View):

    def get(self, request, *args, **kwargs):
        # return redirect('admin/')
        command = ['curl', 'localhost:8000/unlimited-search/?stop=status']
        try:
            res = run(command, capture_output=True, text=True, timeout=0.2)
        except TimeoutExpired:
            messages.success(request, 'error timeout !!!')
        res = loads(res.stdout)

        if res['message'] == 'After Scrap currently page stopped':
            unlimited_status = 'Unlimited Scrap: Already Running'
        elif res['message'] == 'The Program Does not scrap now':
            unlimited_status = 'Unlimited Scrap: Does Not Running'
        else:
            unlimited_status = 'We have A Error, please contact to owner'

        return render(request, 'home/home.html', {'unlimited_status': unlimited_status})


class SearchView(View):

    def get(self, request, *args, **kwargs):
        global time1, session, columns, loop429, number_of_requests, ua, result_message, input_page, start_to_scrap
        session = Session()
        number_of_requests = 0
        loop429 = 0
        time1 = time()
        ua = UserAgent()
        now_datetime = timezone.now()

        try:
            if start_to_scrap:
                return JsonResponse({'message': 'The Program is currently scraping'})
        except NameError:
            start_to_scrap = 1

        try:
            input_page = int(request.GET.get('page'))

        except:
            input_page = -1

        if 0 < input_page <= 199:
            pass
        else:
            input_page = None

        result_message = ''

        print('\nScraper started...\n')

        proxy_list = [
            '78.38.93.22:3128',
            '82.102.26.38:8443',
            '91.107.247.115:4000',
            '138.199.48.1:8443',
            '143.244.60.116:8443'
        ]

        proxies = {
            'http': 'http://' + proxy_list[randint(0, 4)]
            # 'http': 'http://82.102.26.38:8443'
        }

        error = None

        try:
            res = search_in_divar()
        except Exception as e:
            error = format_exc()
            res = []
            # print(error)
            # raise

        process_time = int(time() - time1) // 60

        process_time = f'{process_time // 60} ساعت, {process_time % 60} دقیقه' if process_time > 60 else f'{process_time} دقیقه'

        operation = Operation.objects.create(
            process_time=process_time,
            number_of_requests=number_of_requests,
            number_of_consultants=len(res),
            start_time=now_datetime,
        )

        if error:
            operation.error = error
            operation.is_error = False
            if result_message:
                operation.message = result_message
            operation.save()
        else:
            if result_message:
                operation.message = result_message
                operation.save()

        del start_to_scrap

        return JsonResponse({'message': result_message})


class EnterSearchCommand(View):
    def get(self, request, *args, **kwargs):
        command = ['curl', 'localhost:8000/unlimited-search/']
        try:
            res = run(command, timeout=0.2, capture_output=True, text=True)
        except TimeoutExpired:
            messages.success(request, 'Scraping Started.')
            return redirect('home:home')

        if 'The Program is currently scraping Page' in res.stdout:
            message = loads(res.stdout)['message']
            messages.success(request, message)
            return redirect('home:home')
        else:
            messages.error(request, f'we have a error {res.stdout}')
            return redirect('home:home')


class EnterStopSearchCommand(View):
    def get(self, request, *args, **kwargs):
        command = ['curl', 'localhost:8000/unlimited-search/?stop=true']

        res = run(command, capture_output=True, text=True)
        res = loads(res.stdout)

        messages.success(request, res['message'])
        return redirect('home:home')


class UnlimitedSearchView(View):
    def get(self, request, *args, **kwargs):
        global time1, session, loop429, number_of_requests, ua, result_message, input_page, start_to_scrap_unlimited, stop, process_id

        if request.GET.get('stop') == 'true':
            try:
                stop = stop
                stop = True
                return JsonResponse({'message': 'After Scrap currently page stopped'})
            except NameError:
                return JsonResponse({'message': 'The Program Does not scrap now'})
        elif request.GET.get('stop'):
            try:
                stop = stop
                return JsonResponse({'message': 'After Scrap currently page stopped'})
            except NameError:
                return JsonResponse({'message': 'The Program Does not scrap now'})

        try:
            if start_to_scrap_unlimited:
                stop = False
                return JsonResponse({'message': f'The Program is currently scraping Page {currently_page_number}'})
        except NameError:

            start_to_scrap_unlimited = 1

        stop = False

        session = Session()
        ua = UserAgent()

        number_of_requests = 0
        loop429 = 0

        time1 = time()
        now_datetime = timezone.now()

        result_message = ''

        print('\nScraper started...\n')

        error = None

        try:
            res = unlimited_search_in_divar()
        except Exception as e:
            error = format_exc()
            res = []
            # print(error)
            # raise

        process_time = int(time() - time1) // 60

        process_time = f'{process_time // 60} ساعت, {process_time % 60} دقیقه' if process_time > 60 else f'{process_time} دقیقه'

        operation = Operation.objects.create(
            process_time=process_time,
            number_of_requests=number_of_requests,
            number_of_consultants=number_of_consultants,
            start_time=now_datetime,
        )

        if error:
            operation.error = error
            operation.is_error = False
            if result_message:
                operation.message = result_message
            operation.save()
        else:
            if result_message:
                operation.message = result_message
                operation.save()

        del start_to_scrap_unlimited, stop
        return JsonResponse({'message': result_message})


def get_res(link):
    global columns, number_of_requests, loop429, result_message
    number_of_requests += 1

    try:
        res = session.get(link, timeout=3)
    except (ConnectTimeout, Timeout, ReadTimeout, ConnectionError, SSLError):
        sleep(1)
        return get_res(link)

    print(
        f'{number_of_requests} requests', end='\r')

    if res.status_code not in (429, 500, 501, 502):
        if res.status_code != 200 and res.status_code != 404:
            print('='*90)
            print(res.status_code)
            print(link)
            print('='*90 + '\n')

            result_message += f'''
            
            {'='*90}
            {res.status_code}
            {link}
            {'='*90}
            
            '''
        loop429 = 0
        return res
    elif res.status_code == 429:
        loop429 += 1
        if loop429 >= 3:
            sleep(1)
        sleep(0.4)
        # print('429 HttpError: too many requests'.center(columns), end='\r')
        return get_res(link)
    elif res.status_code >= 500:
        sleep(0.5)
        # print(f'\n{res.status_code} HttpError: server error {link}')

        return get_res(link)


def post_res(link, json=None):
    global number_of_requests, columns

    number_of_requests += 1

    print(
        f'{number_of_requests} requests', end='\r')

    try:
        res = session.post(link, json=json, timeout=3) if json else session.post(
            link, timeout=3)

    except (ConnectTimeout, Timeout, ReadTimeout, ConnectionError, SSLError):
        sleep(1)
        return post_res(link, json)

    if res.status_code == 429:
        sleep(0.5)
        return post_res(link, json)

    return res


def get_ads_of_a_neighbourhood():

    data = {
        "page": 0,
        "json_schema": {
            "category": {"value": "real-estate"},
            "sort": {"value": "sort_date"},
            "districts": {"vacancies": ["40", "1024", "266", "306", "360", "42", "43", "46", "47", "48", "52", "53", "54", "55", "56", "61", "62", "64", "65", "66", "67", "68", "70", "71", "85", "931", "943"]},
            "cities": ["1"],
            "user_type": {"value": "مشاور املاک"},
        },
        # "last-post-date": 1691301438332056
    }

    suggestions = []

    page = 99
    if input_page:
        page = input_page
        print(f'scrap {page} Page')

    for i in range(page):
        global result_message
        data['page'] = i

        res = post_res(
            'https://api.divar.ir/v8/web-search/1/real-estate', json=data)

        try:
            json_res = res.json()
        except Exception as e:
            if str(e) == '[Errno Expecting value] : 0':
                # print('res.text in None')
                # print(res.status_code)
                continue
            print(res.text)
            print(data['page'])
            result_message += f'''
            
            {res.text}
            {data['page']}
            
            '''

        post_list = json_res['web_widgets']['post_list']
        last_post_date = json_res['last_post_date']

        for item in post_list:
            try:
                token = item['data']['token']
            except:
                continue

            link = 'https://divar.ir/v/' + token
            if link not in suggestions:
                suggestions.append(link)

        data['last_post_date'] = last_post_date

    suggestions = get_good_urls(suggestions)

    print(f'The Link of {len(suggestions)} ads obtained')

    return suggestions


def unlimited_get_ads_of_a_neighbourhood():
    global stop, currently_page_number, result_message, number_of_consultants

    data = {
        "page": 0,
        "json_schema": {
            "category": {"value": "real-estate"},
            "sort": {"value": "sort_date"},
            "districts": {"vacancies": ["40", "1024", "266", "306", "360", "42", "43", "46", "47", "48", "52", "53", "54", "55", "56", "61", "62", "64", "65", "66", "67", "68", "70", "71", "85", "931", "943"]},
            "cities": ["1"],
            "user_type": {"value": "مشاور املاک"},
        },
        # "last-post-date": 1691301438332056
    }

    suggestions = []

    stop = False
    currently_page_number = 0

    number_of_consultants = 0

    while not stop:

        data['page'] = currently_page_number

        res = post_res(
            'https://api.divar.ir/v8/web-search/1/real-estate', json=data)

        try:
            json_res = res.json()
        except Exception as e:
            if str(e) == '[Errno Expecting value] : 0':
                # print('res.text in None')
                # print(res.status_code)
                continue
            print(res.text)
            print(data['page'])
            result_message += f'''
            
            {res.text}
            {data['page']}
            
            '''

        post_list = json_res['web_widgets']['post_list']
        last_post_date = json_res['last_post_date']

        for item in post_list:
            try:
                token = item['data']['token']
            except:
                continue

            link = 'https://divar.ir/v/' + token
            if link not in suggestions:
                suggestions.append(link)

        data['last_post_date'] = last_post_date
        currently_page_number += 1

        suggestions = get_good_urls(suggestions)
        print(f'Page {currently_page_number}: suggestions were taken')

        consultants_links = unlimited_get_consultant_link_from_ads(suggestions)
        number_of_consultants += len(consultants_links)
        print(
            f'Page {currently_page_number}: {len(consultants_links)} consultants links obtained' + '\n')

        consultants_information = get_consultant_information(consultants_links)
        print(
            f'Page {currently_page_number}: scrap completed' + '\n')

        suggestions.clear()

    return True


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

    print(f'The Link of {len(result)} consultants obtained' + '\n')
    print(f'Start to get consultants information...' + '\n')

    return result


def unlimited_get_consultant_link_from_ads(ads):

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

    return result


def get_consultant_information(links):
    global number_of_requests

    info = {}
    for link in links:
        url = 'https://api.divar.ir/v8/real-estate/w/agency-public-view'

        agent = link.split('/')[-1]

        def res_options():
            try:
                session.options(url, headers={
                    'Access-Control-Request-Headers': 'content-type', 'Access-Control-Request-Method': 'POST'},
                    timeout=3)
            except (ConnectTimeout, Timeout, ReadTimeout, ConnectionError, SSLError):
                sleep(1)
                return res_options()

        res_options()

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
                    info[agent]['revenue'] = convert_number_to_english_float(
                        item['data']['indicator_text'])

        info[agent]['link'] = link

        ads = get_ads_of_a_consultant(agent)

        info[agent]['ads'] = get_ads_information(ads)

        submit_consultant_data_to_db(agent, info[agent])

        print(
            f'{links.index(link) + 1} - {info[agent]["name"]} - Saved in DB')

    # return True
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

    if noa == 24:
        sub_last_item_identifier = res_json['page']['infinite_scroll_response']['last_item_identifier']
        result = get_ads_of_a_consultant(
            agent, last_item_identifier=sub_last_item_identifier)
        ads.extend(result)

    return ads


def get_ads_information(links):
    global result_message
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

        agency = content.find_all(
            'a', class_='kt-unexpandable-row__action kt-text-truncate')

        if agency:
            if len(agency) == 2 and agency[0] != 'نمایش':
                agency = agency[0]
                result[ads_agent]['agency'] = agency.text
                result[ads_agent]['agency_link'] = 'https://divar.ir' + \
                    agency.attrs['href']

            elif len(agency) > 2 and agency[0].text == 'نمایش':
                agency = agency[1]
                result[ads_agent]['agency'] = agency.text
                result[ads_agent]['agency_link'] = 'https://divar.ir' + \
                    agency.attrs['href']

            elif len(agency) > 2 and agency[0].text != 'نمایش':
                print(
                    f'len of consultant and agency grater than 2\nlink: {link}\nagency: {agency}')
                result_message += f'''
                len of consultant and agency grater than 2\nlink: {link}\nagency: {agency}
                '''.strip()

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
        agencies = []

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

            if v1.get('agency'):
                agency_list = Agency.objects.get_or_create(
                    link=v1.get('agency_link'),
                )
                agency = agency_list[0]
                if agency_list[1]:
                    agency.title = v1['agency']
                    agency.save()
                if agency not in agencies:
                    agencies.append(agency)
                estate.agency = agency
                estate.save()

                agency.consultants.add(consultant)

        consultant.agencies.add(*agencies)
        consultant.scope_of_activity.add(*neighbourhoods)

        size_classification = SizeClassification.objects.filter(
            id__lte=3).order_by('id')

        obj0 = obj1 = obj2 = last = False

        for estate in estates:
            if not estate.size:
                continue

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
        consultant.save()


def search_in_divar():
    global number_of_requests, Session

    number_of_requests = 0

    session.headers.update({
        'User-Agent': ua.random,
        'Origin': 'https://divar.ir',
        'Referer': 'https://divar.ir/',
    })
    session.cookies.update({'pwa-banner-closed': 'true'})

    ads = get_ads_of_a_neighbourhood()
    links = get_consultant_link_from_ads(ads)
    consultant_info = get_consultant_information(links)

    print(f"Number of requests: {number_of_requests}" + '\n')

    return consultant_info


def unlimited_search_in_divar():
    global number_of_requests

    number_of_requests = 0

    session.headers.update({
        'User-Agent': ua.random,
        'Origin': 'https://divar.ir',
        'Referer': 'https://divar.ir/',
    })
    session.cookies.update({'pwa-banner-closed': 'true'})

    ads = unlimited_get_ads_of_a_neighbourhood()

    print(f"Number of requests: {number_of_requests}" + '\n')

    return True


# Thread party functions

def convert_number_to_english(strIn: str):
    global result_message
    P2E_map = {'۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5',
               '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۱': '1',
               "۰": "0", }

    a = map(lambda ch: P2E_map[ch] if ch in P2E_map else '', strIn)
    try:
        return int(''.join(list(a)))
    except Exception as e:
        print('Error int --> ', e)
        result_message += f'''Error --> {e}'''
        return ''.join(list(a))


def convert_number_to_english_float(strIn: str):
    global result_message
    P2E_map = {'۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5',
               '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۱': '1',
               "۰": "0", '،': '.', '.': '.', '٫': '.'}

    a = map(lambda ch: P2E_map[ch] if ch in P2E_map else '', strIn)
    try:
        return float(''.join(list(a)))
    except Exception as e:
        print('Error float --> ', e)
        result_message += f'''Error --> {e}'''
        return ''.join(list(a))
