import jinja2, markdown, os
import datetime as dt
from rich import print

def get_file(src: str) -> str:
    with open(src, 'r') as f:
        content = f.read()
    return content

def write_file(dest: str, content: str) -> None:
    with open(dest, 'w') as f:
        f.write(content)

def get_post_data(src: str) -> tuple[str, str, str, str]:
    # json date, human date, title, content
    mod_time = os.path.getmtime(src)
    json_date = str(dt.date.fromtimestamp(mod_time))
    human_date = str(dt.date.fromtimestamp(mod_time).strftime('%d/%m/%Y'))

    file_content = get_file(src)
    file_lines = file_content.split('\n')

    if file_lines[0][0:2] != '# ':
        raise Exception('malformed post (no first-level header on first line)')
    
    title = file_lines[0].removeprefix('# ')
    content = markdown.markdown('\n'.join(file_lines[1:]), tab_length=4)

    return json_date, human_date, title, content


pages = [
    ['index.html', 'Home'],
    ['projects-content.html', 'Projects & content'],
]
nav = pages + [['weblog/index.html', 'Weblog']]
print(nav)

PATH = 0
NAME = 1

base_template = jinja2.Template(get_file('templates/base.html'))
post_template = jinja2.Template(get_file('templates/post.html'))
post_list = jinja2.Template(get_file('templates/post-index.html'))
navbar = jinja2.Template(get_file('templates/navbar.html'))

print(':page_facing_up: Building static pages...')
for page in pages:
    print(f':hammer: pages/{page[PATH]} ({page[NAME]})')

    try:
        write_file(f'docs/{page[PATH]}', base_template.render(
            title=page[NAME],
            navbar=navbar.render(pages=nav, selected=page),
            content=get_file(f'pages/{page[PATH]}')
        ))
        print(f':white_check_mark: -> docs/{page[PATH]}')
    except Exception as e:
        print(f':x: {e}')
print()

print(':signal_strength: Building posts (last modified first)...')
files = os.listdir('posts')
files.sort(key=lambda x: os.path.getmtime(f'posts/{x}'), reverse=True)
concise_post_data = []
for file in files:
    print(f':hammer: posts/{file}')
    base_name = os.path.basename(file)
    post_id = os.path.splitext(base_name)[0]

    try:
        json_date, human_date, title, content = get_post_data(f'posts/{file}')

        concise_post_data.append([f'{post_id}.html', title, json_date, human_date])

        write_file(f'docs/weblog/{post_id}.html', base_template.render(
            title=title,
            navbar=navbar.render(pages=nav, selected=f'weblog/{file}'),
            content=post_template.render(date=json_date, humandate=human_date, content=content)
        ))

        print(f':white_check_mark: -> docs/weblog/{post_id}.html')
    except Exception as e:
        print(f':x: {e}')
print()

print(':book: Building post list...')
try:
    write_file(f'docs/weblog/index.html', base_template.render(
        title='Weblog',
        navbar=navbar.render(pages=nav, selected=nav[-1]),
        content=post_list.render(posts=concise_post_data)
    ))
    print(f':white_check_mark: -> weblog/index.html')
except Exception as e:
    print(f':x: {e}')