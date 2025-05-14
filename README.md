# ai-project
rasa example project

## 总结

1. rasa的nlu的意图识别和实体标注促使工作集中在训练数据的标注上
2. 知识图谱的引入，保证了系统的后续扩展性的提升
3. 性能卓越，直接准确定位数据。只要意图识别准确，获得的数据就是准确的。白处的要求都可以达到。
4. 架构清晰，分工明确，表单确定下来，总体代码逻辑无需更改。
5. 稳定性还可以，需求后续确认。

纠错； 

## 后续工作
1. 完善对话流程
2. 表单的重新填写（回退？）
3. 训练数据的准备 
4. 全部业务数据的导入
5. 项目的测试
6. 项目的上线
7. 无情形业务场景的支持
8. QA的支持
9. 异常的处理
10. 生成higent的插件
11. 知识图谱的梳理，精细化（办理地点以及所需材料）
12. 测试用例的编写
13. 找到一个可以自动生成训练数据的软件
14. 支持通过输入数字1，2，进行选择下一步,set_ordinal_mention_mapping
15. 按业务模块进行划分，分步上线进行训练

16. 还有一些问题，需要梳理
    - 换证收费吗？（应该和区域无关）
    - 办残疾证要交钱吗？（同上）
    - 是否收费，办理时长，作息时间，都应该和子项相关
    - 残疾证换领情形下，总是有居住地和户籍地的区分

17. 支持一句多问

18. 长语句输入测试

19. 重听 

### 技巧 

1. wait_for_user_input: false
我的残疾证快到期了，咋换新
2. set_ordinal_mention_mapping

### 说明

#### 目前实体的定义如下：

(1)主项名称：main_item

(2)业务办理项名称:business_item

(3)场景：scenario

(4)区域划分：district

(5)详细信息：detail_type

    ①承诺办结时限： 

    ②是否收费：

    ③办理地点：

    ④办理时间：

    ⑤咨询方式：

    受理条件

    办理流程（manual）

    ⑥全部信息

#### 设计了2个表单：

1. 办理材料表单：

需要如下实体：

> (1)主项名称：main_item

> (2)业务办理项名:business_item

> (3)场景：scenario

结果输出： 材料信息

2. 详细信息表单：

> (1)主项名称：main_item

> (2)业务办理项名:business_item

> (3)区域划分

> (4)详细信息选择：
    ①承诺办结时限
    ②是否收费
    ③办理地点
    ④办理时间
    ⑤咨询方式
    ⑥全部信息  


结果：根据用户选择的不同条件，显示不同的信息


### 导入到neo4j的脚本说明

1. 执行 python source/district.py 导入区划
2. 执行 python source/convert_sunlf.py 导入主项等


### 后续任务：

1. 自动化测试工具
2. 自动化数据导入以及数据完整性校验
3. neo4j 索引

### 需要和rasa沟通

1. 我还可以使用 rasa x 辅助开发吗
2. 我有很多的业务实体，包括业务主项、业务办理项，以及这些项目需要的材料。还有办理地点、办理时间等，我需要如何自动创建训练数据，满足rasa可以准确的识别用户的意图呢
3. rasa calm 有什么新的功能特性
4. rasa如何和llm结合呢
5. 我这里的规则都定义在rules.yml文件里，stories.yml什么都没有，这样对吗
6. t_loss=5.72, i_acc=0.983, e_f1=0.972 这些参数说明什么，如何调整


### 数据治理有如下办法

1. 把业务办理项升级为主项名称（公积金为典型）
2. 重新整理业务办理项，重新定义业务主项名称（企业登记注册）
3. 细分业务办理项，针对无情形的业务，把业务办理项较多的业务下放变成情形（企业登记注册）

### 更新测试的业务数据

#### 导入数据到neo4j数据库

1. 复制文件到source/import下

2. 修改207行，使用最新的数据文件

3. 执行 python source/import/fixed_lxw.py && python source/import/rebuild_address.py

4. 执行 python source/import/rebuild_address.py

#### 生成新的nlu训练数据

1. 修改 nlu/import_district.py 12行

2. 修改 nlu/import_data.py 12行

3. 分别运行 ： python source/nlu/import_district.py  和 python source/nlu/import_data.py

4. 文件生成在：data/business 目录

#### 重新训练数据

rasa train 

### 服务器端的更新

1. 登陆后进入 

```
# 更新数据
cd project/ai-project
git pull

# 更新neo4j
python source/import/fixed_lxw.py

# 重新训练 

tmux new -s train
rasa train
ctrl+B D

# 重启 rasa api
tmux a -t rasa-api

# 重启 rasa action
tmux a -t rasa-action

```
124

二楼机关事业单位养

遗属待遇申领 地址是空格分割的


