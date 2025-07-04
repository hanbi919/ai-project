### 

1. 帮我生成10个测试场景,每个场景模拟用户进行多轮提问，模拟老百姓的口气提问 
主业务项：残疾人证办理

子业务项：
    - 残疾人证挂失补办 
    - 残疾人证换领 
    - 残疾人证新办 
详细信息查询：
    - 办理地点   
    - 办理时间
    - 咨询方式
    - 是否收费
    - 承诺办结时限
    - 全部信息
要求：不需要模拟回复

2. 实体标记统一为 detail_type:办理时间，再来20个针对时间的提问

### 安装neo4j工具

上面的两个附件，是通过主项名称和业务办理项名称关联起来的。帮我设计一下知识图谱数据库，使用neo4j。具体内容如下：
    主项名称(MainItem)
    业务办理项名称(BusinessItem)
    情形(Scenario)
    材料(Material)
    行政区划(District)
    办理地点(Location)
    办理时间(Schedule)
    咨询方式(Phone)
    是否收费（Fee）
    承诺办结时限（Deadline）
建立如下关系：
    HAS_BUSINESS_ITEM: 主项名称与业务办理项名称之间的关系
    HAS_SCENARIO: 业务办理项名称与情形之间的关系
    REQUIRES: 情形与所需材料之间的关系
    LOCATED_IN: 业务办理项名称与行政区划之间的关系
    HAS_LOCATION: 行政区划与办理地点之间的关系
    办理地点有四个属性，分别是：办理时间，咨询方式，是否收费，承诺办结时限

请根据上面的设计思想，帮我根据两个文件，生成一个python脚本，可以把两个文件的内容，写入到neo4j数据库里

### 情形的处理

使用rasa设计了一个form，其中情形是一个slot，需要填写。如果这个业务项需要情形，则需要显示情形内容如果不需要，则直接显示所需材料。这个逻辑如何实现，详细说明

### 实现通过数字选择

使用rasa，需要form填写两个slot，第一个是城市选择，数据来自数据库，示例：1.北京，2.上海，3，天津。用户输入数字2，代表选择了上海，然后进入了第二个选择，这个选择的内容也来自数据库，显示：1.2个人，2.3个人，3.4个人，用户选择1，表示是2个人。如何实现上面的功能，可以使用duckling功能


### 区划的知识图谱数据生成

我的数据如上，"上级区划名称"字段的内容，是代表"区划名称"字段的层级关系的，例如："上级区划名称"为“二道区,长春市,吉林省”，"区划名称"为东站街道，代表东站街道属于吉林省，长春市，二道区，按照这个逻辑，帮我建立一个neo4j数据库，生成python代码来创建。
要求：如果区划名称重复，那么只要层级关系是不重复的，就需要新创建node

### 基础信息最终

上面的附件，是通过主项名称和业务办理项名称关联起来的。帮我设计一下知识图谱数据库，使用neo4j。具体内容如下：
    1.主项名称(MainItem)
    2.业务办理项名称(BusinessItem)
    3.情形(Scenario)
    4.材料(Material)
    5.区划名称(District)
    6.办理地点(Location)

建立如下关系：
    HAS_BUSINESS_ITEM: 主项名称与业务办理项名称之间的关系
    HAS_SCENARIO: 业务办理项名称与情形之间的关系
    REQUIRES: 情形与所需材料之间的关系
    LOCATED_IN: 业务办理项名称与区划名称(District)之间的关系
    HAS_LOCATION: 区划名称(District)与办理地点之间的关系
    办理地点有四个属性，分别是：办理时间，咨询方式，是否收费，承诺办结时限，受理条件


其中：区划名称是已经有的数据，需要根据主项名称与业务办理项名称，找到对应的区划名称，才可以建立关系
请根据上面的设计思想，帮我根据文件，生成一个python脚本，可以把文件的内容，写入到neo4j数据库里

### 生成cypher脚本

我在neo4j里面有一个节点location，另外一个节点address，location-》has_address-address。我想模糊查询address，location和address是一对多的关系。我如何通过对address模糊查询，获得多条数据，同时我也希望可以让location的属性也同时返回结果，如何实现

mcp-flight-search/
├── mcp_flight_search/
│   ├── __init__.py              # Package initialization and exports
│   ├── config.py                # Configuration variables (API keys)
│   ├── models/
│   │   ├── __init__.py          # Models package init
│   │   └── schemas.py           # Pydantic models (FlightInfo)
│   ├── services/
│   │   ├── __init__.py          # Services package init
│   │   ├── search_service.py    # Main flight search logic
│   │   └── serpapi_client.py    # SerpAPI client wrapper
│   ├── utils/
│   │   ├── __init__.py          # Utils package init
│   │   └── logging.py           # Logging configuration
│   └── server.py                # MCP server setup and tool registration
├── main.py                      # Main entry point
├── pyproject.toml               # Python packaging configuration
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
