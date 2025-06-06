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


SANIC_WORKERS=12 rasa run --enable-api --cors "*" --debug

### 压力测试

ab -n 400 -c 20 -p data.json -T "application/json" http://localhost:5005/webhooks/rest/webhook > test_results.txt

ab -n 400 -c 20 -p data.json -T "application/json" -l -k http://localhost:5005/webhooks/rest/webhook > test_results.txt

nohup ab -n 400 -c 20  -t 60 -p data.json -T "application/json" -l -k http://localhost:5005/webhooks/rest/webhook > test_results.txt 2>&1 &
ab -n 10 -c 1

nohup ab -n 400 -c 20 -p data.json -T "application/json" -l -k http://localhost:5005/webhooks/rest/webhook > test_results.txt 2>&1 &


### neo4j

docker exec -it neo4j cypher-shell -u neo4j -p password


docker run --name neo4j   -p 7474:7474 -p 7687:7687   -v neo4j_data:/data   -v neo4j_logs:/logs   -v neo4j_import:/var/lib/neo4j/import   --env NEO4J_AUTH=neo4j/password  --env NEO4J_dbms_connector_bolt_thread__pool__min__size=20 --env NEO4J_dbms_connector_bolt_thread__pool__max__size=50 --env NEO4J_dbms_memory_heap_initial__size=1G  --env NEO4J_dbms_memory_heap_max__size=2G --env NEO4J_dbms_memory_pagecache_size=4G --env NEO4J_dbms_memory_heap_initial__size=2G --env NEO4J_dbms_memory_heap_max__size=4G --restart unless-stopped --memory 16g --cpus 8  -d neo4j:latest 


### rasa run 

SANIC_WORKERS=8 \
SANIC_ACCESS_LOG=false \
SANIC_REQUEST_MAX_SIZE=100000000 \
SANIC_REQUEST_TIMEOUT=120 \
rasa run \
  --enable-api \
  --cors "*" \
  --model models/latest.tar.gz \
  --endpoints endpoints.yml \
  --credentials credentials.yml \
  --log-file rasa.log \
  --debug \
  --port 5006



  ### rasa 集群

  rasa run --enable-api --cors "*" --port 5007 --debug

  ```
  upstream rasa_cluster {
    # 配置所有Rasa实例
    server localhost:5006;  # 实例1
    server localhost:5007;  # 实例2
    server localhost:5008;  # 实例3
    
    # 会话保持(同一用户分配到同一后端)
    # ip_hash;
    hash $http_x_sender_id consistent; 
    # 健康检查
    keepalive 32;
  }

  server {
    listen 5005;
    server_name 192.168.213.65;

    location / {
      proxy_pass http://rasa_cluster;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      
      # 重要超时设置
      proxy_connect_timeout 300s;
      proxy_read_timeout 300s;
      proxy_send_timeout 300s;
      
      # WebSocket支持
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
    }
  }

```

ln -s /etc/nginx/sites-available/rasa.conf /etc/nginx/sites-enabled/

### rasa actions

export ACTION_SERVER_SANIC_WORKERS=12
ACTION_SERVER_SANIC_WORKERS=12 rasa run  actions --debug


