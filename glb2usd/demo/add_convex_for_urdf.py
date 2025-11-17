import os
from os.path import join
import re
pattern = r'<mesh filename=\"textured_objs/(.*?).obj\"/>'
def add_convex(urdf_path):
    with open(urdf_path, 'r') as urdf_file:
        urdf_text = urdf_file.read()
    urdf_file.close()
    matches = list(re.finditer(pattern, urdf_text, re.DOTALL))
    add_num = 0
    for i, match in enumerate(matches):
        if i % 2 == 1:
            urdf_text = urdf_text[:match.end()-7+add_num*7] + "_convex" + urdf_text[match.end()-7+add_num*7:]
            add_num += 1

    with open(urdf_path, 'w') as urdf_file:
        urdf_file.write(urdf_text)
    urdf_file.close()
    return

urdfs = './urdfs'
for cat in os.listdir(urdfs):
    cat_path = join(urdfs, cat)
    for urdf in os.listdir(cat_path):
        urdf_path = join(join(cat_path, urdf), f'{urdf}.urdf')
        with open(urdf_path, 'r') as file:
            text = file.read()
        file.close()
        text = text.replace('_convex', '')
        with open(urdf_path, 'w') as file:
            file.write(text)
        file.close()
        add_convex(urdf_path)
