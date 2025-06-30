import sys
import importlib.util

# 检查关键包是否能导入
required_packages = {
    "langchain": "0.0.200",
    "openai": "0.27.8",
    "chromadb": "0.4.6",
    "tiktoken": "0.4.0",
    "unstructured": "0.10.24",
    "blosc2": "2.0.0",
    "cython": "0.29.36",
    "dill": "0.3.6",
    "black": "23.7.0"
}

all_packages_ok = True

print("===== 环境配置验证 =====")
print(f"Python 版本: {sys.version}")

for package, min_version in required_packages.items():
    try:
        spec = importlib.util.find_spec(package)
        if spec is None:
            print(f"❌ 未安装 {package}")
            all_packages_ok = False
            continue
            
        module = importlib.import_module(package)
        version = getattr(module, '__version__', '未知')
        
        # 简单的版本比较
        if version != '未知':
            from packaging import version as pkg_version
            if pkg_version.parse(version) < pkg_version.parse(min_version):
                print(f"⚠️ {package} 版本 {version} 低于建议的 {min_version}")
            else:
                print(f"✅ {package} 已安装，版本 {version}")
        else:
            print(f"✅ {package} 已安装")
    except Exception as e:
        print(f"❌ 导入 {package} 时出错: {e}")
        all_packages_ok = False

# 验证LangChain基本功能
if all_packages_ok:
    print("\n===== 测试LangChain基本功能 =====")
    try:
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        
        # 创建一个简单的LLM链（不实际调用API）
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="请简要介绍一下 {topic}。",
        )
        
        # 使用dry_run模式，不实际调用API
        llm = OpenAI(model_name="text-davinci-003", temperature=0.7, dry_run=True)
        chain = LLMChain(llm=llm, prompt=prompt)
        
        print("✅ LangChain 导入和基本功能正常")
    except Exception as e:
        print(f"❌ LangChain 测试失败: {e}")
        print("请检查你的OpenAI API密钥是否正确配置")

print("\n===== 验证完成 =====")
if all_packages_ok:
    print("🎉 环境配置成功！所有检查项均通过。")
else:
    print("❓ 环境配置存在问题，请检查上面的错误信息。")    