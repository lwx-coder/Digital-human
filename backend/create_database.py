import pymysql
import sys

def create_database():
    """
    创建MySQL数据库
    """
    try:
        print("尝试连接到MySQL服务器...")
        # 连接MySQL服务器
        connection = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="123456",
            connect_timeout=10
        )
        
        print("成功连接到MySQL服务器")
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS digitalhuman CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("数据库'digitalhuman'创建成功！")
        
        # 检查数据库是否创建成功
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("MySQL服务器上的数据库列表:")
        for db in databases:
            print(f" - {db[0]}")
            
        # 关闭连接
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")
        
    except Exception as e:
        print(f"连接MySQL服务器时出错: {e}")
        print("请确保MySQL服务已启动，并且用户名和密码正确")
        sys.exit(1)

if __name__ == "__main__":
    create_database() 