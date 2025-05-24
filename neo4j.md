方法 1：通过 APT 安装（推荐）
1. 添加 Neo4j 官方 GPG 密钥
bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
2. 添加 Neo4j APT 仓库
bash
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
3. 更新软件包索引
bash
sudo apt update
4. 安装 Neo4j（社区版/企业版）
社区版（免费）：

bash
sudo apt install neo4j
企业版（需许可证）：

bash
sudo apt install neo4j-enterprise
5. 启动 Neo4j 服务
bash
sudo systemctl enable neo4j  # 设置开机自启
sudo systemctl start neo4j   # 立即启动
6. 验证服务状态
bash
sudo systemctl status neo4j

