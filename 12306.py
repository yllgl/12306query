# !/user/bin/env python
# -*- coding:utf-8 -*-

import requests, re, time, ssl, urllib
from urllib import parse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import urllib3

urllib3.disable_warnings() #不显示警告信息
ssl._create_default_https_context = ssl._create_unverified_context
req = requests.Session()

# 获取RAIL_DEVICEID写在登录之前get_rail_deviceid()函数
# req.cookies['RAIL_DEVICEID'] = 'ng8GWpVBAs1dnOxtsAEnQ1EyfbEuCIGetci8OLRrXAtY_grSokW5WZb10aDdNS_Je4KbKlgf3fPtO4cZJGCox4ORGXGZ8Fhcq6TDWW1iuLlaU2kLccvL22V_HBd49idoCqL0dJEbfl3Plhhno73VZqQY5aKeAHHJ'
def unicode_to_percent_u(unicode_string):
    # Encode the unicode string to its percent-encoded form with 'unicode-escape' to get '\uXXXX' for each character
    escaped_str = unicode_string.encode('unicode-escape').decode()
    
    # Replace the '\u' with '%u' and remove the 'b' character at the start
    percent_u_str = escaped_str.replace('\\u', '%u').replace('b\'', '').replace('\'', '')
    
    # For the comma, since it's a single byte character, manually add its percent-encoded form
    percent_u_str = percent_u_str.replace(',', '%2C')
    
    return percent_u_str

from datetime import datetime, timedelta

def adjust_date(date_str, days):
    """
    Adjust the given date by a certain number of days.

    :param date_str: The date in 'YYYY-MM-DD' format.
    :param days: The number of days to adjust the date by. Can be negative.
    :return: A new date in 'YYYY-MM-DD' format.
    """
    date_format = '%Y-%m-%d'
    original_date = datetime.strptime(date_str, date_format)
    new_date = original_date + timedelta(days=days)
    return new_date.strftime(date_format)
class Leftquery(object):
    '''余票查询'''

    def __init__(self):
        self.station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9002'
        self.headers = {
            "Accept": "*/*",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "zh-CN,zh;q=0.9",
"Cache-Control": "no-cache",
"Connection": "keep-alive",
"Cookie":"_jc_save_fromStation={}{}; _jc_save_toStation={}{}; _jc_save_fromDate={}; _jc_save_toDate={}; _jc_save_wfdc_flag=dc",
"Host": "kyfw.12306.cn",
"If-Modified-Since": "0",
"Referer": "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E7%8E%89%E6%9E%97,YLZ&ts=%E6%B7%B1%E5%9C%B3,IOQ&date=2023-12-23&flag=N,N,Y",
"Sec-Fetch-Dest": "empty",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-origin",
"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
"X-Requested-With": "XMLHttpRequest",
"sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
"sec-ch-ua-mobile": "?1",
"sec-ch-ua-platform": '"Android"'
}
        self.station_name_dict = None
        self.station_name_dict2 = None
    def station_name(self, station):
        '''获取车站简拼'''
        html = requests.get(self.station_url, verify=False).text
        result = html.split('@')[1:]
        if self.station_name_dict is None:
            dict = {}
            for i in result:
                key = str(i.split('|')[1])
                value = str(i.split('|')[2])
                dict[key] = value
            self.station_name_dict = dict
            self.station_name_dict2 = {value:key for (key,value) in dict.items()}
        else:
            return self.station_name_dict[station]
        return dict[station]

    def query(self, from_station, to_station, date,trainNumber=None):
        '''余票查询'''
        fromstation = self.station_name(from_station)
        tostation = self.station_name(to_station)
        url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            date, fromstation, tostation)
        # 学生票查询: url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=0X00'.format(date, fromstation, tostation)
        try:
            tmpheaders = self.headers.copy()
            tmpheaders['Cookie'] = self.headers['Cookie'].format(unicode_to_percent_u(from_station+","),fromstation,unicode_to_percent_u(to_station+","),tostation,date, date)
            html = requests.get(url, headers=tmpheaders, verify=False).json()
            result = html['data']['result']
            if result == []:
                print('很抱歉,没有查到符合当前条件的列车!')
                exit()
            else:
                print(date + from_station + '-' + to_station + '查询成功!')
                if trainNumber:
                    def f(x):
                        info = self.parse_ticket_info(x)
                        if info["train_no"]==trainNumber:
                            return True
                        else:
                            return False
                    result = list(filter(lambda x:f(x),result))
            return result
        except Exception as e:
            print('查询信息有误!请重新输入!')
            print('出发地:' + fromstation + ' 目的地:' + tostation + ' 出发日期:' + date)
            print(e)
            exit()

    def queryStation(self, from_station, to_station, date, trainNumber):
        "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=80000K12060V&from_station_telecode=YLZ&to_station_telecode=BJQ&depart_date=2023-12-26"
        fromstation = self.station_name(from_station)
        tostation = self.station_name(to_station)
        url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={}&from_station_telecode={}&to_station_telecode={}&depart_date={}'.format(
            trainNumber, fromstation, tostation, date)
        try:
            tmpheaders = self.headers.copy()
            tmpheaders['Cookie'] = self.headers['Cookie'].format(unicode_to_percent_u(from_station+","),fromstation,unicode_to_percent_u(to_station+","),tostation,date, date)
            html = requests.get(url, headers=tmpheaders, verify=False).json()
            result = html['data']['data']
            if result == []:
                print('很抱歉,没有查到符合当前条件的列车!')
                exit()
            else:
                print(date + from_station + '-' + to_station + '查询成功!')
                # 打印出所有车次信息
                print(result)
                idx = 0
                before_station = []
                after_station = []
                fromdate = 0
                adate = None
                while idx<len(result):
                    station = result[idx]
                    if idx>0 and self.parse_duration(station['start_time'])<self.parse_duration(result[idx-1]['start_time']):
                        fromdate+=1
                    idx+=1
                    if station['station_name'] == from_station:
                        adate = fromdate
                        before_station.append((station["station_name"],fromdate))
                        break
                    else:
                        before_station.append((station["station_name"],fromdate))
                while idx<len(result) and result[idx]['station_name']!=to_station:
                    if idx>0 and self.parse_duration(result[idx]['start_time'])<self.parse_duration(result[idx-1]['start_time']):
                        fromdate+=1
                    idx+=1
                while idx<len(result):
                    station = result[idx]
                    if idx>0 and self.parse_duration(station['start_time'])<self.parse_duration(result[idx-1]['start_time']):
                        fromdate+=1
                    idx+=1
                    if station['station_name'] == to_station:
                        after_station.append(station["station_name"])
                        continue
                    else:
                        after_station.append(station["station_name"])
                print("before_station",before_station,"after_station",after_station)
                result = []
                for (bstation,day) in before_station:
                    for astation in after_station[::-1]:
                        if bstation!=from_station or astation!=to_station:
                            tmpresult = self.query(bstation, astation, adjust_date(date,day-adate),trainNumber=trainNumber)
                            if tmpresult:
                                result.extend(tmpresult)
                return result
        except Exception as e:
            print(e)
    def parse_ticket_info(self, ticket_str):
        '''解析票价和余票信息'''
        ticket_data = ticket_str.split('|')
        train_info = {
            'train_no': ticket_data[2],  # 火车参数
            'train_code': ticket_data[3],  # 车次
            'from_station_code': ticket_data[6],  # 出发地代号
            'to_station_code': ticket_data[7],  # 目的地代号
            'from_station_no': ticket_data[16],  # 发车地代号
            'to_station_no': ticket_data[17],  # 终点代号
            'seat_types': ticket_data[35],  # 座位类型
            'start_time': ticket_data[8],  # 出发时间
            'end_time': ticket_data[9],  # 到站时间
            'duration_time': ticket_data[10],  # 持续时间
            'business_seat': ticket_data[32]  or '--',  # 商务座/特等座
            'first_seat': ticket_data[31] or '--',  # 一等座
            'second_seat': ticket_data[30] or '--',  # 二等座
            'high_sleep': ticket_data[21] or '--',  # 高级软卧
            'soft_sleep': ticket_data[23] or '--',  # 软卧
            'dong_sleep': ticket_data[33] or '--',  # 动卧
            'hard_sleep': ticket_data[28] or '--',  # 硬卧
            'soft_seat': ticket_data[24] or '--',  # 软座
            'hard_seat': ticket_data[29] or '--',  # 硬座
            'no_seat': ticket_data[26] or '--',  # 无座
            'price_info': ticket_data[39],  # 价格信息
            'special_shop_seat': ticket_data[25] or '--',
            "origin_ticket_str":ticket_str
        }
        # print(train_info)
        return train_info
    def parse_duration(self, duration_str):
        '''解析时长字符串'''
        hours, minutes = map(int, duration_str.split(':'))
        return hours + minutes / 60

    def time_plus_duration(self, start_time, duration):
        '''计算出发时间加上持续时间'''
        start_hours, start_minutes = map(int, start_time.split(':'))
        total_hours = start_hours + duration
        return total_hours
    def query_and_sort_tickets(self, from_station, to_station, date):
        '''查询并按价格排序余票'''
        seat_types_dict = {
            'no_seat': 'WZ',         # 无座
            'hard_seat': '1',        # 硬座
            'soft_seat': '2',        # 软座
            'second_seat': 'O',      # 二等座
            'first_seat': 'M',       # 一等座
            'special_shop_seat': 'P',# 特等座
            'hard_sleep': '3',       # 硬卧
            'soft_sleep': '4',       # 软卧
            'dong_sleep': 'D',       # 动卧（这里假设代号是D，实际上可能需要根据具体情况调整）
            'high_sleep': '6',       # 高级软卧
            'business_seat': '9'     # 商务座
        }

        tickets = self.query(from_station, to_station, date)
        parsed_tickets = [self.parse_ticket_info(ticket) for ticket in tickets]
        add_tickets = []
        # 筛选和排序余票
        sorted_tickets = []
        parsed_tickets2 = []
        for ticket in parsed_tickets:
            duration = self.parse_duration(ticket['duration_time'])
            total_time = self.time_plus_duration(ticket['start_time'], duration)

            if duration <= 1:  # 1小时以内
                seat_types = ['no_seat','hard_seat', 'soft_seat', 'second_seat', 'first_seat','hard_sleep', 'soft_sleep', 'dong_sleep', 'high_sleep','special_shop_seat','business_seat']  # 无座或以上
            elif 1 < duration <= 8 and total_time <= 24:  # 1小时以上8小时以内且未经过半夜12点
                seat_types = ['hard_seat', 'soft_seat', 'second_seat', 'first_seat','hard_sleep', 'soft_sleep', 'dong_sleep', 'high_sleep','special_shop_seat','business_seat']  # 硬座或以上
            else:  # 超过8小时或过半夜
                seat_types = ['hard_sleep', 'soft_sleep', 'dong_sleep', 'high_sleep','special_shop_seat','business_seat']  # 硬卧或以上
            tmp = self.queryStation(self.station_name_dict2[ticket["from_station_code"]], self.station_name_dict2[ticket["to_station_code"]], date, ticket["train_no"])
            def f(x):
                info = self.parse_ticket_info(x)
                info["original_from_station_code"] = ticket["from_station_code"]
                info["original_to_station_code"] = ticket["to_station_code"]
                info["original_start_time"] = ticket["start_time"]
                info["original_end_time"] = ticket["end_time"]
                return info
            tmp = list(map(lambda x:f(x),tmp))
            parsed_tickets2.extend(tmp)
            available_tickets = {}
            for seat_type in seat_types:
                if ticket[seat_type] and ticket[seat_type] != '--' and ticket[seat_type] != '无':  # 检查余票
                    # 解析价格信息
                    print("ticket[seat_type] 1:",ticket[seat_type])
                    if len(ticket['price_info'])%10==0:
                        for k in range(len(ticket['price_info'])//10):
                            match = re.search(r"%s(\d{4})(\d{5})"%(seat_types_dict[seat_type]), ticket['price_info'][k*10:(k+1)*10])
                            if match:
                                price = int(match.group(1))
                                available_tickets[seat_type] = price
                                break
            
            # 如果有可用票务信息，则添加到结果中
            if available_tickets:
                ticket['available_tickets'] = available_tickets
                sorted_tickets.append(ticket)
        for ticket in parsed_tickets2:
            available_tickets = {}
            for seat_type in seat_types:
                if ticket[seat_type] and ticket[seat_type] != '--' and ticket[seat_type] != '无':  # 检查余票
                    # 解析价格信息
                    print("ticket[seat_type] 2:",ticket[seat_type])
                    if len(ticket['price_info'])%10==0:
                        for k in range(len(ticket['price_info'])//10):
                            match = re.search(r"%s(\d{4})(\d{5})"%(seat_types_dict[seat_type]), ticket['price_info'][k*10:(k+1)*10])
                            if match:
                                price = int(match.group(1))
                                available_tickets[seat_type] = price
                                break
            
            # 如果有可用票务信息，则添加到结果中
            if available_tickets:
                ticket['available_tickets'] = available_tickets
                sorted_tickets.append(ticket)
        sorted_tickets.sort(key=lambda x: min(x['available_tickets'].values()))

        return sorted_tickets


if __name__ == '__main__':
    q = Leftquery()
    sorted_tickets = q.query_and_sort_tickets("深圳","长春","2024-01-05")
    mapping_seattype2CH = {"no_seat":"无座","hard_seat":"硬座","soft_seat":"软座","second_seat":"二等座","first_seat":"一等座","hard_sleep":"硬卧","soft_sleep":"软卧","dong_sleep":"动卧","high_sleep":"高级软卧","special_shop_seat":"特等座","business_seat":"商务座"}
    final_result = []
    for ticket in sorted_tickets:
        for seat_type,price in ticket['available_tickets'].items():
            final_result.append((ticket,seat_type,price))
    if len(final_result)==0:
        print("没有找到符合条件的车次")
        exit()
    final_result.sort(key=lambda x:x[2])
    for ticket,seat_type,price in final_result:
        if "original_from_station_code" in ticket:
            print("车次{} {}-{}(原{}-{} 出发时间：{}到达时间：{}){}价格{}元".format(ticket["train_code"],q.station_name_dict2[ticket["from_station_code"]],q.station_name_dict2[ticket["to_station_code"]],q.station_name_dict2[ticket["original_from_station_code"]],q.station_name_dict2[ticket["original_to_station_code"]],ticket["original_start_time"],ticket["original_end_time"],mapping_seattype2CH[seat_type],price))
        else:
            print("车次{} {}-{} 出发时间：{}到达时间：{} {}价格{}元".format(ticket["train_code"],q.station_name_dict2[ticket["from_station_code"]],q.station_name_dict2[ticket["to_station_code"]],ticket["start_time"],ticket["end_time"],mapping_seattype2CH[seat_type],price))