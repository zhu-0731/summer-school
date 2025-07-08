import pandas as pd
import re
from typing import List, Tuple, Dict


def parse_answer_string(answer_string: str) -> List[Tuple[int, str]]:
    """
    解析类似 "1-b,2-a,3-b,4-b..." 格式的字符串
    
    Args:
        answer_string: 包含问题序号和答案的字符串
        
    Returns:
        包含 (问题序号, 答案) 元组的列表
    """
    # 分割字符串并解析每个部分
    items = answer_string.strip().split(',')
    parsed_answers = []
    
    for item in items:
        item = item.strip()
        if '-' in item:
            # 使用正则表达式提取数字和字母
            match = re.match(r'(\d+)-([a-zA-Z]+)', item)
            if match:
                question_num = int(match.group(1))
                answer = match.group(2).upper()  # 转换为大写
                parsed_answers.append((question_num, answer))
    
    return parsed_answers


def create_table_from_answers(answer_string: str, columns_per_row: int = 10) -> pd.DataFrame:
    """
    将答案字符串转换为表格格式
    
    Args:
        answer_string: 包含问题序号和答案的字符串
        columns_per_row: 每行显示的问题数量
        
    Returns:
        pandas DataFrame 格式的表格
    """
    parsed_answers = parse_answer_string(answer_string)
    
    # 创建字典来存储数据
    data = {}
    
    # 创建行数据
    rows = []
    current_row = {}
    
    for i, (question_num, answer) in enumerate(parsed_answers):
        col_name = f"Q{question_num}"
        current_row[col_name] = answer
        
        # 每达到指定列数或最后一个答案时，添加到行列表
        if (i + 1) % columns_per_row == 0 or i == len(parsed_answers) - 1:
            rows.append(current_row)
            current_row = {}
    
    # 创建DataFrame
    df = pd.DataFrame(rows)
    
    # 填充空值
    df = df.fillna('')
    
    return df


def create_vertical_table(answer_string: str) -> pd.DataFrame:
    """
    创建垂直格式的表格（问题号-答案两列）
    
    Args:
        answer_string: 包含问题序号和答案的字符串
        
    Returns:
        pandas DataFrame 格式的表格
    """
    parsed_answers = parse_answer_string(answer_string)
    
    df = pd.DataFrame(parsed_answers, columns=['问题序号', '答案'])
    return df


def display_table_styles(df: pd.DataFrame, title: str = "答案表格"):
    """
    以不同样式显示表格
    
    Args:
        df: pandas DataFrame
        title: 表格标题
    """
    print(f"\n=== {title} ===")
    print(df.to_string(index=False))
    
    print(f"\n=== {title} (Markdown格式) ===")
    print(df.to_markdown(index=False))


def calculate_scores(answer_string: str) -> Dict[str, int]:
    """
    根据答案字符串计算每列的得分

    Args:
        answer_string: 包含问题序号和答案的字符串

    Returns:
        每列的得分字典
    """
    # 定义表格映射
    scoring_table = {
        "E": [1, 5, 9, 13, 17, 21, 25, 29, 33, 37],
        "I": [2, 6, 10, 14, 18, 22, 26, 30, 34, 38],
        "S": [1, 5, 9, 13, 17, 21, 25, 29, 33, 37],
        "N": [2, 6, 10, 14, 18, 22, 26, 30, 34, 38],
        "T": [3, 7, 11, 15, 19, 23, 27, 31, 35, 39],
        "F": [4, 8, 12, 16, 20, 24, 28, 32, 36, 40],
        "J": [3, 7, 11, 15, 19, 23, 27, 31, 35, 39],
        "P": [4, 8, 12, 16, 20, 24, 28, 32, 36, 40],
    }

    # 解析答案字符串
    parsed_answers = parse_answer_string(answer_string)
    answer_dict = {q: a for q, a in parsed_answers}

    # 计算得分
    scores = {key: 0 for key in scoring_table.keys()}
    for trait, questions in scoring_table.items():
        for q in questions:
            if q in answer_dict and answer_dict[q] == "B":
                scores[trait] += 1

    return scores


def main():
    # 示例数据
    answer_string = "1-b,2-b,3-a,4-b,5-b,6-a,7-a,8-b,9-b,10-a,11-b,12-a,13-b,14-b,15-b,16-b,17-b,18-b,19-a,20-a,21-a,22-b,23-a,24-a,25-b,26-a,27-b,28-b,29-a,30-a,31-b,32-a,33-b,34-b,35-a,36-a,37-a,38-a,39-a,40-a"
    
    print("原始答案字符串:")
    print(answer_string)
    print("\n" + "="*80)
    
    # 方式1: 水平表格 (每行4个问题，总共10行)
    horizontal_table = create_table_from_answers(answer_string, columns_per_row=4)
    display_table_styles(horizontal_table, "水平表格 (每行4题，总共10行)")
    
    # 计算得分
    scores = calculate_scores(answer_string)
    print("\n得分:")
    for trait, score in scores.items():
        print(f"{trait}: {score}")
    
    # # 方式2: 水平表格 (每行5个问题)
    # horizontal_table_5 = create_table_from_answers(answer_string, columns_per_row=5)
    # display_table_styles(horizontal_table_5, "水平表格 (每行5题)")
    
    # # 方式3: 垂直表格
    # vertical_table = create_vertical_table(answer_string)
    # display_table_styles(vertical_table, "垂直表格")
    
    # 保存为CSV文件
    try:
        horizontal_table.to_csv('answers_horizontal.csv', index=False, encoding='utf-8-sig')
        print(f"\n表格已保存为CSV文件:")
        print("- answers_horizontal.csv (水平格式)")
    except Exception as e:
        print(f"保存CSV文件时出错: {e}")

    # 保存为Excel文件
    try:
        # 创建一一对应的格式表格
        index_answer_table = create_vertical_table(answer_string)
        with pd.ExcelWriter('answers_tables.xlsx', engine='openpyxl') as writer:
            index_answer_table.to_excel(writer, sheet_name='Index_Answer', index=False)
        print("- answers_tables.xlsx (Excel格式，包含Index_Answer工作表)")
    except Exception as e:
        print(f"保存Excel文件时出错: {e}")
        print("提示: 如需保存Excel文件，请安装openpyxl: pip install openpyxl")

    # 格式化输出表格
    formatted_table = horizontal_table.fillna('')
    print("\n最终表格格式:")
    print(formatted_table.to_string(index=False))


def process_custom_string(custom_string: str):
    """
    处理用户自定义的答案字符串
    
    Args:
        custom_string: 用户输入的答案字符串
    """
    print(f"\n处理自定义字符串: {custom_string}")
    print("="*50)
    
    # 创建表格
    horizontal_table = create_table_from_answers(custom_string, columns_per_row=8)
    vertical_table = create_vertical_table(custom_string)
    
    # 显示结果
    display_table_styles(horizontal_table, "水平表格")
    display_table_styles(vertical_table, "垂直表格")
    
    return horizontal_table, vertical_table


def process_multiple_strings(answer_strings: List[str]):
    """
    处理多个答案字符串并保存到Excel文件

    Args:
        answer_strings: 包含多个答案字符串的列表
    """
    # 添加输入数据检查
    if not answer_strings or not all(answer_strings):
        print("输入数据为空或格式不正确，请检查后重试。")
        return

    all_tables = []

    for i, answer_string in enumerate(answer_strings):
        print(f"\n处理第{i + 1}个字符串: {answer_string}")
        print("=" * 50)

        # 创建表格
        horizontal_table = create_table_from_answers(answer_string, columns_per_row=4)
        index_answer_table = create_vertical_table(answer_string)

        # 添加到结果列表
        all_tables.append((f"String_{i + 1}_Horizontal", horizontal_table))
        all_tables.append((f"String_{i + 1}_Index_Answer", index_answer_table))

    # 保存到Excel文件
    try:
        with pd.ExcelWriter('answers_multiple_strings.xlsx', engine='openpyxl') as writer:
            for sheet_name, table in all_tables:
                table.to_excel(writer, sheet_name=sheet_name, index=False)
        print("- answers_multiple_strings.xlsx (Excel格式，包含多个工作表)")
    except Exception as e:
        print(f"保存Excel文件时出错: {e}")
        print("提示: 如需保存Excel文件，请安装openpyxl: pip install openpyxl")


if __name__ == "__main__":
    main()
    
    # 交互式功能
    print("\n" + "="*80)
    print("您可以输入自己的答案字符串进行转换:")
    print("格式示例: 1-a,2-b,3-c,4-a...")
    print("输入 'quit' 退出程序")
    
    while True:
        user_input = input("\n请输入答案字符串: ").strip()
        if user_input.lower() == 'quit':
            print("程序结束!")
            break
        elif user_input:
            try:
                process_custom_string(user_input)
            except Exception as e:
                print(f"处理出错: {e}")
                print("请检查输入格式是否正确")
        else:
            print("输入不能为空，请重新输入")

    # 示例数据
    answer_strings = [
        "1-b,2-a,3-b,4-b,5-b,6-a,7-b,8-b,9-b,10-a,11-b,12-b,13-b,14-b,15-b,16-b,17-b,18-b,19-a,20-b,21-a,22-a,23-a,24-b,25-b,26-a,27-a,28-b,29-a,30-b,31-b,32-a,33-b,34-b,35-a,36-a,37-b,38-b,39-b,40-b",
        "1-b,2-b,3-a,4-a,5-b,6-a,7-a,8-b,9-b,10-a,11-a,12-a,13-b,14-b,15-b,16-a,17-a,18-b,19-a,20-b,21-a,22-b,23-a,24-b,25-b,26-a,27-a,28-b,29-a,30-b,31-b,32-a,33-b,34-b,35-a,36-a,37-b,38-a,39-b,40-a",
        "1-b,2-b,3-a,4-b,5-b,6-a,7-a,8-b,9-b,10-a,11-b,12-a,13-b,14-b,15-b,16-b,17-b,18-b,19-a,20-a,21-a,22-b,23-a,24-a,25-b,26-a,27-b,28-b,29-a,30-a,31-b,32-a,33-b,34-b,35-a,36-a,37-a,38-a,39-a,40-a"
    ]

    process_multiple_strings(answer_strings)