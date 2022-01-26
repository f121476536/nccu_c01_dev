import sys

def find_char_position_in_string(string, char):
        position = []
        n = 0
        while(n != -1):
            n = string.find(char, n + 1)
            if(n != -1):
                position.append(n)
        return position

start_tag = '<a>'
end_tag = '</a>'

string = '我的回答是<a>國立政治大學(https://3kkofdskfsjd)</a>，謝謝!'
string = string.replace(start_tag, '').replace(end_tag, '')

omit_flag = False
result = ''
for char in string:
    if char == '(':
        omit_flag = True
    elif char == ')':
        omit_flag = False
        continue
    if(not omit_flag):
        result += char

print(result)