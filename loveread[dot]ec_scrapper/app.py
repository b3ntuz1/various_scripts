import lxml
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs

from ebooklib import epub

url = "http://loveread.ec/read_book.php?id=62726&p=1"
toc = []
title = 'Intro'
dic = {}
dic[title] = ''


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


def get_chapters(soup):
    ''' повертає словарь де ключ це назва розділу, а значення -- це зміст. '''
    ''' потрібно зробити:
    1. знаходити та зберігати картинки
    2. розрізняти розмітку тексту курсив, жирний і т.д
    3. почистити від старої html розмітки
        1. видалити зайві css, класи і т.д
    '''
    global title
    global dic
    for s in soup.contents:
        if (s.name == 'div'):
            # знайти заголовок
            if s.attrs.get('class') == ['take_h1']:
                title = s.get_text(strip=True)
                dic[title] = '<h2>' + title + '</h2>\n<br />'
                toc.append(title)
            # рекурсія
            get_chapters(s)
            continue
        # знайти текст
        if (s.name == 'p'):
            dic[title] += s.get_text(strip=True) + '\n<br />'


def build_book(book_title, authors):
    # building the book
    book = epub.EpubBook()
    book.set_identifier('some_id')
    book.set_title(book_title)
    book.set_language('ru')
    
    for author in authors:
        book.add_author(author)
    spine = [] 
    for k in toc:
        file_name = k.replace(' ', '_') + '.html' 
        chapter = epub.EpubHtml(title=k, file_name=file_name)
        chapter.set_content(dic[k])
        spine.append(chapter)
        book.add_item(chapter)
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

    build_book(book_title, authors)

if __name__ == '__main__':
    main()

