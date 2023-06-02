import requests
import pandas as pd
import datetime
import ast


class Group:
    def __init__(self, is_closed, activity, age_limits, members_count, trending, verified, wall):
        self.is_closed = 'открытое' if is_closed == 0 else 'закрытое' if is_closed == 1 else 'частное'
        self.activity = activity
        self.age_limits = '0+' if age_limits == 1 else '16+' if age_limits == 2 else '18+'
        self.members_count = members_count
        self.trending = trending
        self.verified = verified
        self.wall = 'выключена' if wall == 0 else 'открытая' if wall == 1 else ' ограниченная' if wall == 2 else 'закрытая'


def get_info_about_group(group_name, access_token):
    group = requests.get('https://api.vk.com/method/groups.getById?' +
                         'group_id=' +
                         group_name +
                         '&' +
                         'v=5.131&' +
                         'fields=activity,age_limits,ban_info,members_count,trending,verified,wall&' +
                         'access_token=' + access_token).json()['response'][0]
    # 0 — открытое; 1 — закрытое; 2 — частное. | очевидно нужно 0
    is_closed = group['is_closed'] == 0
    # Строка тематики паблика. |куча разных, выбирать под тип рекламы (реклама магазина техники - тематика "техника")
    activity = group['activity']
    # 1 — нет; 2 — 16+; 3 — 18+ | предпочтительно 1
    age_limits = group['age_limits']
    # число подписчиков | чем больше - чем лучше
    members_count = group['members_count']
    # Информация о том, есть ли у сообщества «огонёк». | больше охват если есть
    trending = group['trending']
    # 1 — является; 0 — не является. | больше охват
    verified = group['verified']
    # 0 — выключена;1 — открытая;2 — ограниченная;3 — закрытая. | если 1 то много мусора но можно и самому бесплатно оставлять рекламу
    wall = group['wall']
    return Group(is_closed, activity, age_limits, members_count, trending, verified, wall)

class AgrUser():
    def __init__(self,mean_age, city, active_core, active_core_perc, mean_follow, follow_threshhold, follow_threshhold_perc,
            male_perc, verified_perc, trend_perc):
        self.mean_age = mean_age
        self.city = city
        self.active_core = active_core
        self.active_core_perc = active_core_perc
        self.mean_follow = mean_follow
        self.follow_threshhold = follow_threshhold
        self.follow_threshhold_perc = follow_threshhold_perc
        self.male_perc = male_perc
        self.verified_perc = verified_perc
        self.trend_perc = trend_perc


def analyze_user(group_name, access_token):
    next_from = '0'
    mass = []
    count = 0
    while next_from != '':
        print('Обработка пользователей от ' + str(count * 1000) + ' до ' + str((count + 1) * 1000 - 1))
        group_members = requests.get('https://api.vk.com/method/groups.getMembers?' +
                                     'group_id=' + group_name + '&' +
                                     'v=5.131&' +
                                     'fields=deactivated&'
                                     'start_from=' + next_from +
                                     '&access_token=' + access_token).json()['response']
        mass.extend(group_members['items'])
        next_from = group_members['next_from']
        count = count + 1

    next_from = '0'
    batch_size = 1000
    user_info = []
    count = 0
    while count <= len(mass) // batch_size + 1:
        print('Обработка пользователей от ' + str(count * batch_size) + ' до ' + str((count + 1) * batch_size - 1))
        group_members = requests.post('https://api.vk.com/method/users.get?' +
                                      'user_ids=' + str(
            [x.get('id') for x in mass[count * batch_size:(count + 1) * batch_size - 1]]) + '&' +
                                      'v=5.131&' +
                                      'fields=bdate,city,followers_count,last_seen,relation,personal,sex,trending,verified&'
                                      '&access_token=' + access_token).json()['response']
        user_info.extend(group_members)
        count = count + 1
    df_user_info = pd.DataFrame.from_records(user_info)
    df_user_inf_del_closed_prof = df_user_info.drop(
        ['first_name', 'last_name', 'can_access_closed', 'is_closed', 'relation_partner'], axis=1)
    df_user_inf_del_closed_prof['bdate'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                             int(str(
                                                                                 x['bdate']).split(
                                                                                 '.')[2]) if len(
                                                                                 str(x[
                                                                                         'bdate'])) > 5 else None,
                                                                             axis=1)
    df_user_inf_del_closed_prof['city'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                            str(str(x['city']).split(
                                                                                'title')[1].split(
                                                                                '\'')[2]) if type(x[
                                                                                                      'city']) != float else None,
                                                                            axis=1)
    df_user_inf_del_closed_prof['last_seen'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                                 (
                                                                                     datetime.datetime.fromtimestamp(
                                                                                         int(x[
                                                                                             'last_seen'].get(
                                                                                             'time')))) if len(
                                                                                     str(x[
                                                                                             'last_seen'])) > 5 else None,
                                                                                 axis=1)
    df_user_inf_del_closed_prof['alcohol'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                               (ast.literal_eval(str(
                                                                                   x[
                                                                                       'personal']))).get(
                                                                                   'alcohol') if len(
                                                                                   str(x[
                                                                                           'personal'])) > 5 else None,
                                                                               axis=1)
    df_user_inf_del_closed_prof['life_main'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                                 (ast.literal_eval(
                                                                                     str(x[
                                                                                             'personal']))).get(
                                                                                     'life_main') if len(
                                                                                     str(x[
                                                                                             'personal'])) > 5 else None,
                                                                                 axis=1)
    df_user_inf_del_closed_prof['people_main'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                                   (ast.literal_eval(
                                                                                       str(x[
                                                                                               'personal']))).get(
                                                                                       'people_main') if len(
                                                                                       str(x[
                                                                                               'personal'])) > 5 else None,
                                                                                   axis=1)
    df_user_inf_del_closed_prof['political'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                                 (ast.literal_eval(
                                                                                     str(x[
                                                                                             'personal']))).get(
                                                                                     'political') if len(
                                                                                     str(x[
                                                                                             'personal'])) > 5 else None,
                                                                                 axis=1)
    df_user_inf_del_closed_prof['smoking'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                               (ast.literal_eval(str(
                                                                                   x[
                                                                                       'personal']))).get(
                                                                                   'smoking') if len(
                                                                                   str(x[
                                                                                           'personal'])) > 5 else None,
                                                                               axis=1)
    df_user_inf_del_closed_prof['religion'] = df_user_inf_del_closed_prof.apply(lambda x:
                                                                                (ast.literal_eval(str(
                                                                                    x[
                                                                                        'personal']))).get(
                                                                                    'religion') if len(
                                                                                    str(x[
                                                                                            'personal'])) > 5 else None,
                                                                                axis=1)
    df_user_inf_del_closed_prof = df_user_inf_del_closed_prof.drop(['personal'], axis=1)
    mean_age = datetime.date.today().year - df_user_inf_del_closed_prof['bdate'].mean()  # средний возраст
    city = df_user_inf_del_closed_prof['city'].mode()[0]  # город по моде
    active_core = len([x for x in df_user_inf_del_closed_prof['last_seen'] if
                       (pd.Timestamp.now() - x).days <= 7])  # сколько подписчиков заходили за последние 7 дней
    active_core_perc = active_core / len(df_user_inf_del_closed_prof) * 100  # процент предыдущего
    mean_follow = df_user_inf_del_closed_prof[
        'followers_count'].mean()  # среднее количество фолловеров у подписчика
    follow_threshhold = len(df_user_inf_del_closed_prof[df_user_inf_del_closed_prof[
                                                            "followers_count"] >= 1000.0])  # количество подписчиков у которых 1000+ фолловеров
    follow_threshhold_perc = follow_threshhold / len(df_user_inf_del_closed_prof) * 100  # процент предыдущего
    male_perc = len(df_user_inf_del_closed_prof[df_user_inf_del_closed_prof["sex"] == 2]) / len(
        df_user_inf_del_closed_prof) * 100  # процент лиц мужского пола
    verified_perc = len(
        df_user_inf_del_closed_prof[df_user_inf_del_closed_prof["verified"] == 1]) / len(
        df_user_inf_del_closed_prof) * 100  # процент верифицированных подписчиков
    trend_perc = len(df_user_inf_del_closed_prof[df_user_inf_del_closed_prof["trending"] == 1]) / len(
        df_user_inf_del_closed_prof) * 100  # процент подписчиков с "огоньком"
    return AgrUser(mean_age, city, active_core, active_core_perc, mean_follow, follow_threshhold, follow_threshhold_perc,
            male_perc, verified_perc, trend_perc)
