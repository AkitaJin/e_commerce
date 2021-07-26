# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---
#%%
# # 电商数据分析
# ## 数据读入

import pandas as pd
import matplotlib.pyplot as plt

filepath = r'../data/data.csv'
raw = pd.read_csv(filepath, encoding="ISO-8859-1")
raw.head()

# ## 数据预处理



raw.info()

df1 = raw.copy()
#简单去重
df1 = df1.drop_duplicates()
#暂不考虑产品描述
df1.drop(["Description"],axis = 1, inplace=True)
#缺失值处理
df1["CustomerID"] = df1["CustomerID"].fillna("unknown")
#修改数据类型
df1["CustomerID"] = df1["CustomerID"].astype("str")
# df1[df1.CustomerID != df1.CustomerID]
# set(df1.CustomerID)
df1

#异常值查看
df1.describe()

# 负数的数量为退货，负数的价格定义为异常。



df1 = df1[df1["UnitPrice"] >= 0]

# 数据类型处理



df1["Total"]=df1["Quantity"]*df1["UnitPrice"]
df1[["Date","Time"]]=df1["InvoiceDate"].str.split(" ",expand=True)
df1[["Month","Day","Year"]] = df1["Date"].str.split("/",expand=True)
df1["Hour"]=df1["Time"].str.split(":",expand=True)[0].astype("int")
df1

#将全部数据分为数量>=0的购买数据和数量<0的退货数据
data_buy = df1[df1["Quantity"] >= 0]
data_return = df1[df1["Quantity"] < 0]

# ## 帮助函数



def dist_cum_p(gp, bins):
    gp_dist = pd.cut(gp,bins=bins).value_counts().sort_index()
    tmp1 = gp_dist/gp_dist.sum()
    tmp2 = gp_dist.cumsum()/gp_dist.sum()
    dist_cum_p = pd.concat([tmp1,tmp2], axis=1)
    dist_cum_p.columns=['bin_%', 'bin_%_cum']
    return dist_cum_p

# ## 商品维度分析
# ### 最热卖的产品是哪些？退货最多的产品是哪些？



df2 = df1.copy()
df2

product_quantity = df2["Quantity"].groupby(df2["StockCode"]).sum().sort_values(ascending=False)
product_quantity.head(10)

product_quantity.tail(10)

# ### 商品的价格分布如何？价格与销量有何关系？



df2.UnitPrice.describe()

data_unique_stock=df2.drop_duplicates(["StockCode"])
data_unique_stock["UnitPrice"].describe()

# 该电商网站以销售低价商品为主。商品价格的中位数远大于平均数，是一个右偏分布，即该网站售卖的绝大部分都是低价商品，极少部分商品价格高昂，导致商品价格的标准差较大。

# +
#分组的区间，左开右闭
bins = [0,1,2,3,4,5,6,7,10,15,20,25,30,100,10000,20000,30000,40000]

# price_bin=pd.cut(data_unique_stock["UnitPrice"],bins=bins).value_counts().sort_index()
# price_per=price_bin/price_bin.sum()
# price_cumper=price_bin.cumsum()/price_bin.sum()
# price_dist = pd.concat([price_per,price_cumper],axis=1)
# price_dist.columns=['bin_%', 'bin_%_cum']
price_dist = dist_cum_p(data_unique_stock["UnitPrice"], bins)
price_dist
# -

price_dist['bin_%_cum'].plot()

# 具体来看，商品价格在（1，2]的价格区间里是最多的,占23.19%；商品价格在10元以内的占了93.28%，在100元以内的占了99.79%。

cut=pd.cut(df2["UnitPrice"],bins=bins)
quantity_price=df2["Quantity"].groupby(cut).sum()
qpd = round(quantity_price/quantity_price.sum(),6)
quant_price_dist = quantity_price.cumsum()/quantity_price.sum()
qpdp = pd.concat([qpd,quant_price_dist],axis=1)
qpdp

quant_price_dist.plot()

# 71.68%的商品销量集中在价格在2元以内的商品；99.7%的商品销量集中的价格在15元以内的商品。

# ### 退货商品的价格分布与退货量情况是怎样的？

# +
data_return_unique_stock=data_return.drop_duplicates("StockCode")
# return_cut=pd.cut(data_return_unique_stock["UnitPrice"],bins=[0,1,2,3,4,5,10,15,20,50,100,200,500,1000]).value_counts().sort_index()
# pd.concat([return_cut/return_cut.sum(),return_cut.cumsum()/return_cut.sum()],axis=1)

bins_3=[0,1,2,3,4,5,10,15,20,50,100,200,500,1000]
return_dist = dist_cum_p(data_return_unique_stock["UnitPrice"], bins_3)
return_dist
# -

# 退货商品最多的价格区间是（1，2]元，退货商品价格在10元以内的占了95.46%。

# +

return_dist['bin_%'].plot()
qpd.plot()
# -

# 红色是退货商品的价格分布，蓝色是全部商品的价格分布。从退货商品种类的角度，退货商品与总体商品相比，更集中在0-3元与5-10元这两个区间。

return_quantity_price=data_return["Quantity"].groupby(pd.cut(data_return["UnitPrice"],bins=[0,1,2,3,4,5,10,15,20,50,100,200,500,1000])).sum()
return_quantity_price/return_quantity_price.sum()

(return_quantity_price/return_quantity_price.sum()).plot()
(quantity_price/quantity_price.sum()).plot()

# 1-10元的商品退货量会偏高一些。







# ## 顾客维度分析

# ### 哪些顾客购买金额最多？

customer_total=data_buy["Total"].groupby(data_buy["CustomerID"]).sum().sort_values(ascending=False)
customer_total.head(11)

# 缺失客户ID的订单占比很大，后续分析可能有问题。

# ### 哪些顾客购买次数最频繁？

customer_buy_fre=data_buy.drop_duplicates(["InvoiceNo"])["InvoiceNo"].groupby(data_buy["CustomerID"]).count().sort_values(ascending=False)
customer_buy_fre[:20]

# ### 如何根据这两个变量对顾客分类？

customer_total.drop("unknown",inplace=True)
customer_buy_fre.drop("unknown",inplace=True)

plt.style.use("ggplot")
plt.scatter(customer_buy_fre.sort_index(),customer_total.sort_index())
plt.axhline(y=50000,c="green")
plt.axvline(x=50,c="blue")

# 可以根据顾客购买次数和购买金额，对顾客进行分组，采取不同的营销措施。

# ### 订单的商品种类分布是怎样的？

order_type=data_buy["StockCode"].groupby(data_buy["InvoiceNo"]).count().sort_values(ascending=False)
# stock_dist = pd.cut(order_type,bins=[0,50,100,150,200,250,300,500,1000,1200]).value_counts()
# tmp1 = stock_dist/stock_dist.sum()
# tmp2 = stock_dist.cumsum()/stock_dist.sum()
# stock_dist_cum_p = pd.concat([tmp1,tmp2], axis=1)
# stock_dist_cum_p.columns=['bin_%', 'bin_%_cum']




bins_2 = [0,50,100,150,200,250,300,500,1000,1200]
dist_cum_p(order_type,bins_2)

order_type_r=data_return["StockCode"].groupby(data_return["InvoiceNo"]).count().sort_values(ascending=False)
pd.cut(order_type_r,bins=[0,10,20,30,40,50,60,150]).value_counts()

# 退货顾客的商品种类大部分都在10以内。

# ### 哪些国家的顾客消费占比最大？

# +
country_total = df2["Total"].groupby(df2["Country"]).sum().sort_values(ascending=False)
country_customer=df2["CustomerID"].groupby(df2["Country"]).count().sort_values(ascending=False)
country_total_percent=(country_total/country_total.sum())
country_total_percent

# country_customer
# -







# ### 哪些国家的顾客数量最多？







# ### 哪些国家的顾客平均消费最高？









# ## 时间维度分析













# ## 汇总分析













# %%
