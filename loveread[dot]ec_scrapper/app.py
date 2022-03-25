import lxml
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs

from ebooklib import epub

# url = "http://loveread.ec/read_book.php?id=62726&p=1"
url = 'http://loveread.ec/read_book.php?id=6240&p=1'
title = 'Intro'
toc = []
toc.append(title)
dic = {}
dic[title] = title
img_list = []


def get_html(url):
    ''' отримує url та повертає html '''
    req = Request(url)
    html = urlopen(req).read()
    return html


def get_max_page_num(nav):
    ''' Поверне число що описує кількість сторінок в книжці '''
    nav = nav.find('div', class_='navigation')
    max_num = 0
    for i in nav.find_all('a'):
        url = i.get('href')
        num = int(parse_qs(urlparse(url).query)['p'][0])
        max_num = num if num > max_num else max_num
    return max_num


def get_image(imgurl):
    '''
    1. отримати imgurl
    2. завантажити картинку
    3. зформувати новий img тег
    4. додати ім'я файлу картинки та бінарні дані у глобальний список
       для подальшої обробки
    '''
    global img_list
    with urlopen(imgurl) as rh:
        img_data = rh.read()
    img_name = imgurl.split('/')[-1]
    img_tag = f'<img src="{img_name}" />'
    img_list.append({'img_data': img_data, 'img_name': img_name})
    return img_tag


def clear_data(data):
    data = str(data).replace(' class="MsoNormal"', '')
    return data.strip()


def get_chapters(soup):
    ''' повертає словарь де ключ це назва розділу, а значення -- це зміст. '''
    global title
    global dic
    for s in soup.contents:
        if (s.name == 'form'):
            continue
        if (s.name == 'div'):
            # фільтрує навігацію з сайту, як правило, це кінець документу
            if (s.attrs.get('class') == ['navigation']):
                break
            # знайти заголовок
            if s.attrs.get('class') == ['take_h1']:
                title = s.get_text(strip=True)
                dic[title] = '<h2>' + title + '</h2>\n'
                toc.append(title)
            # рекурсія
            get_chapters(s)
            continue
        # знайти текст
        if (s.name == 'img'):
            src = s.get('src')
            dic[title] += get_image(f'http://loveread.ec/{src}')
            continue
        if (s.name == 'p'):
            dic[title] += f'{clear_data(s)}\n'


def build_book(book_title, authors, cover):
    # building the book
    book = epub.EpubBook()
    book.set_identifier('some_id')
    book.set_title(book_title)
    book.set_language('ru')

    cover = cover.select('div.MsoNormal p:nth-child(2) img:nth-child(1)')
    book.set_cover('cover.jpg', urlopen(f'http://loveread.ec/{cover[0].attrs.get("src")}').read())
    
    for author in authors.split(', '):
        book.add_author(author)

    spine = [] 
    for k in toc:
        file_name = k.replace(' ', '_') + '.html' 
        chapter = epub.EpubHtml(title=k, file_name=file_name)
        chapter.set_content(dic[k])
        spine.append(chapter)
        book.add_item(chapter)

    for img in img_list:
        i = epub.EpubImage()
        i.file_name = img['img_name']
        i.media_type = 'image/jpeg'
        i.set_content(img['img_data'])
        book.add_item(i)

    book.toc = spine
    book.spine = spine
    epub.write_epub(book_title.replace(' ', '_') + '.epub', book)


def main():
    '''
    1. в циклі обійти всі сторінки книжки
    2. з кожної сторінки отримати об'єкт soup з текстом книги
    3. передати soup для аналізу
    4. зібрати всі дані в книжку
    '''
    print('start parsing the book')
    print('-'*100)
    html = BeautifulSoup(get_html(url), 'lxml')

    book_title, authors, _ = html.find('title').get_text('|', strip=True).split(' | ')
    print(f'title: {book_title}\nauthor(s): {authors}')

    nav = get_max_page_num(html)
    print(f'pages: {nav}')
    print('-'*100)

    for i in range(1, nav):
        urlpage = url[:-1] + str(i)
        soup = BeautifulSoup(get_html(urlpage), 'lxml').select('.tb_read_book div:nth-child(4)')
        get_chapters(soup[0])

    build_book(book_title, authors, html)

if __name__ == '__main__':
    main()

