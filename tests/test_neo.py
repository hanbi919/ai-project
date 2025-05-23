import asyncio
from neo4j import AsyncGraphDatabase
import time
import random
import matplotlib.pyplot as plt
from collections import defaultdict

# Neo4j 连接配置
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")  # 替换为您的实际密码

# 测试查询
CYPHER_QUERY = """
MATCH (m:MainItem {name: $main_item})
USING INDEX m:MainItem(name)
MATCH (b:BusinessItem {name: $business_item})
USING INDEX b:BusinessItem(name)
MATCH (m)-[:HAS_BUSINESS_ITEM]->(b)-[:LOCATED_IN]->(s:District)
RETURN s.name AS district
ORDER BY s.name
"""

# 测试参数
QUERY_PARAMS = {
    'main_item': '变更工伤登记',
    'business_item': '无',
    'scenario': '无情形'
}


async def run_query(driver, query, params):
    """执行单个查询并返回耗时"""
    start_time = time.time()
    async with driver.session() as session:
        result = await session.run(query, params)
        records = await result.values()
    elapsed = (time.time() - start_time) * 1000  # 毫秒
    return elapsed, len(records)


async def worker(driver, query, params, concurrency_level, results):
    """并发工作线程"""
    elapsed, count = await run_query(driver, query, params)
    results[concurrency_level].append(elapsed)


async def performance_test(concurrency_levels, iterations_per_level):
    """执行性能测试"""
    driver = AsyncGraphDatabase.driver(URI, auth=AUTH)

    # 预热连接
    await run_query(driver, CYPHER_QUERY, QUERY_PARAMS)

    results = defaultdict(list)

    for concurrency in concurrency_levels:
        print(f"测试并发级别: {concurrency}")

        tasks = []
        for _ in range(iterations_per_level):
            task = worker(driver, CYPHER_QUERY,
                          QUERY_PARAMS, concurrency, results)
            tasks.append(task)

        # 使用gather来并发执行
        await asyncio.gather(*tasks)

    await driver.close()
    return results


def analyze_results(results):
    """分析并可视化结果"""
    avg_times = []
    throughputs = []

    for concurrency, times in sorted(results.items()):
        avg_time = sum(times) / len(times)
        throughput = (concurrency * 1000) / avg_time  # 每秒查询数

        print(
            f"并发 {concurrency}: 平均响应时间 {avg_time:.2f}ms, 吞吐量 {throughput:.2f} QPS")

        avg_times.append(avg_time)
        throughputs.append(throughput)

    # 绘制图表
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(sorted(results.keys()), avg_times, 'b-o')
    plt.xlabel('并发级别')
    plt.ylabel('平均响应时间 (ms)')
    plt.title('响应时间 vs 并发级别')

    plt.subplot(1, 2, 2)
    plt.plot(sorted(results.keys()), throughputs, 'g-o')
    plt.xlabel('并发级别')
    plt.ylabel('吞吐量 (QPS)')
    plt.title('吞吐量 vs 并发级别')

    plt.tight_layout()
    plt.savefig('neo4j_performance.png')
    plt.show()


async def main():
    # 测试配置
    concurrency_levels = [1, 5, 10, 20, 50, 100]  # 测试的并发级别
    iterations_per_level = 100  # 每个并发级别执行的次数

    print("开始性能测试...")
    results = await performance_test(concurrency_levels, iterations_per_level)
    print("测试完成，分析结果...")
    analyze_results(results)

if __name__ == "__main__":
    asyncio.run(main())
