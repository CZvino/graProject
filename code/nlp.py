# -*- coding:utf-8 -*-

import sys
import jieba
import jieba.analyse

def get_segment(content):
    return jieba.cut(content)

def get_keyword(content, top_k):
    return jieba.analyse.extract_tags(content, topK=top_k)

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    s = ("蚂蚁金服旗下的支付宝，是以每个人为中心，拥有超4.5亿实名用户的生活服务平台。目前，支付宝已发展成为融合了支付、生活服务、政务服务、社交、理财、保险、公益等多个场景与行业的开放性平台。除提供便捷的支付、转账、收款等基础功能外，还能快速完成信用卡还款、充话费、缴水电煤等！通过智能语音机器人一步触达上百种生活服务，不仅能享受消费打折，跟好友建群互动，还能轻松理财，累积信用，让生活更简单！【官方微博】@支付宝 http://weibo.com/zfbwxzf 【主要功能】1、支持余额宝，理财收益随时查看；2、支持各种场景关系，群聊群付更方便；3、提供本地生活服务，买单打折尽享优惠；4、为子女父母建立亲情账户；5、随时随地查询淘宝账单、账户余额、物流信息；6、免费异地跨行转账，信用卡还款、充值、缴水电煤气费；7、还信用卡、付款、缴费、充话费、卡券信息智能提醒；8、行走捐，支持接入iPhone健康数据，可与好友一起健康行走及互动，还可以参与公益。")
    seg_list = jieba.cut(s)
    print "Full Mode:", "/ ".join(seg_list)
    key_list = get_keyword(s, 10)
    print ",".join(key_list)

if __name__ == "__main__":
    main()
