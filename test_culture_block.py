import re

# 模拟文化块处理
accepted_cultures = ['nanfaren', 'manchu', 'yankee']
formatted_content = '\n\t\t' + '\n\t\t'.join([f'"{item}"' for item in accepted_cultures])
new_block_content = f'culture=\n\t{{\n\t\t{formatted_content}\n\t}}'

print('生成的文化块内容:')
print(repr(new_block_content))
print()
print('格式化后的内容:')
print(new_block_content)
