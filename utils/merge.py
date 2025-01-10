import pandas as pd
import argparse
import os

# 读取 JSONL 文件
def read_jsonl(file_path):
    return pd.read_json(file_path, lines=True)

def main(base_file):
    # 提取 base 文件的目录和文件名
    base_dir = os.path.dirname(base_file)
    base_name = os.path.splitext(os.path.basename(base_file))[0]

    # 定义其他文件路径
    house_file = os.path.join("output", base_name, base_name + '_house_cleaned.jsonl')
    neighbor_file = os.path.join("output", base_name, base_name + '_neighbor_cleaned.jsonl')
    svi_file = os.path.join("output", base_name, base_name + '_svi_cleaned.jsonl')

    # 输出文件路径
    output_dir = os.path.join("output", base_name)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, base_name + '_merged.jsonl')

    # 读取每个文件
    df_house = read_jsonl(house_file)
    df_neighbor = read_jsonl(neighbor_file)
    df_svi = read_jsonl(svi_file)
    df_base = read_jsonl(base_file)

    # 合并数据框（通过 'id' 列）
    merged_df = df_base
    merged_df = merged_df.merge(df_house, on='id', how='left')
    merged_df = merged_df.merge(df_neighbor, on='id', how='left')
    merged_df = merged_df.merge(df_svi, on='id', how='left')

    # 保存合并后的结果
    merged_df.to_json(output_file, orient='records', lines=True)
    print(f"合并完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge JSONL files by ID")
    parser.add_argument('--base_file', type=str, required=True, help="Path to base JSONL file")

    args = parser.parse_args()

    main(args.base_file)
