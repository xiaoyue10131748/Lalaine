import pandas as pd

from purpose_prediction.utils_traffic import TRAFFIC_TEST_FLAG

# App Functionality
# Analytics
# Third-Party Advertising
# Developer's Advertising or Marketing
ad_list = ['ad ', 'adverti', 'bid', 'banner', 'promot']
developer_marketing_list = ['push', 'notification']
analyze_list = ['analy', 'mining',
                'risk', 'machine learning', 'big data', 'attribut', 'refer', 'log', 'stats', 'statistic', 'track', 'idfa', 'ip,', 'event']
person_list = ['fountain', 'flow', 'recommend', 'personalization', 'customi',
               'feature', 'card', 'anonym', 'page']

PREDICT_TEST_FLAG = False


def judge_third_party_ad(df: pd.DataFrame) -> tuple:
    domain_category = df['domain_category']
    FP_list = ['crm']
    if isinstance(domain_category, str):
        domain_category = domain_category.lower()
        for fp in FP_list:
            if fp in domain_category:
                return False, '', ''
        for ad in ad_list:
            if ad in domain_category:
                return True, 'Third-Party Advertising', ad
    return False, '', ''


def judge_analytics(df: pd.DataFrame) -> tuple:
    QB_keys = df['QB_keys']
    if isinstance(QB_keys, str):
        QB_keys = QB_keys.lower().split(',')
        for key in QB_keys:
            if 'analy' in key:
                return True, 'Analytics', key
        if len(QB_keys) > 10:
            return True, 'Analytics', 'QB_keys'

    domain_category = df['domain_category']
    if isinstance(domain_category, str):
        domain_category = domain_category.lower()
        for analyze in analyze_list:
            if analyze in domain_category:
                return True, 'Analytics', analyze

    domain = df['domain']
    if domain in ['facebook']:
        return True, 'Analytics', domain

    return False, '', ''


def judge_developer_ad(df: pd.DataFrame) -> tuple:
    argkeys = QH_keys = QB_keys = path = ''
    if isinstance(df['url_arg_keys'], str):
        argkeys = df['url_arg_keys'].lower()
    if isinstance(df['QH_keys'], str):
        QH_keys = df['QH_keys'].lower()
    if isinstance(df['QB_keys'], str):
        QB_keys = df['QB_keys'].lower()
    if isinstance(df['path'], str):
        path = df['path'].lower()

    for ad in ad_list:
        if ad in argkeys or ad in QH_keys or ad in QB_keys or ad in path:
            return True, 'Developer\'s Advertising or Marketing', ad
    for mkt in developer_marketing_list:
        if mkt in argkeys or mkt in QH_keys or mkt in QB_keys or mkt in path:
            return True, 'Developer\'s Advertising or Marketing', mkt

    return False, '', ''


def judge_personalization(df: pd.DataFrame) -> tuple:
    argkeys = QH_keys = QB_keys = path = ''
    if isinstance(df['url_arg_keys'], str):
        argkeys = df['url_arg_keys'].lower()
    if isinstance(df['QH_keys'], str):
        QH_keys = df['QH_keys'].lower()
    if isinstance(df['QB_keys'], str):
        QB_keys = df['QB_keys'].lower()
    if isinstance(df['path'], str):
        path = df['path'].lower()
    for person in person_list:
        if person in argkeys or person in QH_keys or person in QB_keys or person in path:
            return True, 'Product Personalization', person

    SB_type = df['SB_type']
    if isinstance(SB_type, str):
        if 'html' in SB_type:
            return True, 'Product Personalization', 'SB_type'
    return False, '', ''


def predict_line(df: pd.DataFrame) -> tuple:
    is_third_party_ad, type, reason = judge_third_party_ad(df)
    if is_third_party_ad:
        return type, reason

    is_developer_ad, type, reason = judge_developer_ad(df)
    if is_developer_ad:
        return type, reason

    is_analytics, type, reason = judge_analytics(df)
    if is_analytics:
        return type, reason

    is_personalization, type, reason = judge_personalization(df)
    if is_personalization:
        return type, reason

    if TRAFFIC_TEST_FLAG:
        return '', ''
    else:
        return 'App Functionality', ''
