"""Pytest fixtures and HTML mock data."""

from __future__ import annotations

import pytest


@pytest.fixture
def gdz_main_html() -> str:
    return """
    <html>
    <body>
      <div class="layout">
        <div class="page">
          <aside>
            <div class="sidebar__main">
              <div>
                <ul>
                  <li>
                    <a>1 класс</a>
                    <ul>
                      <li><a href="/class-1/">Все предметы</a></li>
                      <li><a href="/class-1/matematika/">Математика</a></li>
                      <li><a href="/class-1/russkiy_yazyk/">Русский язык</a></li>
                    </ul>
                  </li>
                  <li>
                    <a>2 класс</a>
                    <ul>
                      <li><a href="/class-2/">Все предметы</a></li>
                      <li><a href="/class-2/matematika/">Математика</a></li>
                    </ul>
                  </li>
                </ul>
              </div>
            </div>
          </aside>
          <main>
            <table>
              <tbody>
                <tr>
                  <td class="table-section-heading"><a href="/matematika/">Математика</a></td>
                </tr>
                <tr>
                  <td class="table-section-heading"><a href="/biologiya/">Биология</a></td>
                </tr>
              </tbody>
            </table>
          </main>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def gdz_books_html() -> str:
    return """
    <html>
    <body>
      <div>
        <div class="page">
          <main>
            <ul class="book__list">
              <li>
                <a href="/class-1/matematika/moro/" title="Учебник по математике 1 класс Моро">
                  <div>
                    <p><span>Моро М.И., Волкова С.И.</span></p>
                  </div>
                </a>
              </li>
              <li>
                <a href="/class-1/matematika/peterson/" title="Математика 1 класс Петерсон">
                  <div>
                    <p><span>Петерсон Л.Г.</span></p>
                  </div>
                </a>
              </li>
            </ul>
          </main>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def gdz_pages_html() -> str:
    return """
    <html>
    <body>
      <div>
        <div class="page">
          <main>
            <div class="task__list js-tasks-container">
              <div><a href="/class-1/matematika/moro/1-prt-1/">1</a></div>
              <div><a href="/class-1/matematika/moro/1-prt-2/">2</a></div>
            </div>
          </main>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def gdz_solution_html() -> str:
    return """
    <html>
    <body>
      <div class="layout">
        <div class="page">
          <main>
            <figure>
              <div class="task-img-container">
                <div>
                  <img src="//gdz.ru/attachments/images/tasks/000/011/936/0000/sample.jpg" alt="Номер 1" />
                </div>
              </div>
            </figure>
          </main>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def euroki_main_html() -> str:
    return """
    <html>
    <body>
      <div id="menuwka_new">
        <ul class="primary">
          <li>
            <a href="/gdz/ru/vse/11_klass">11 класс</a>
            <ul>
              <li class="sbjcts"><a href="/gdz/ru/algebra/11_klass" title="Алгебра">Алгебра</a></li>
            </ul>
          </li>
        </ul>
      </div>
      <div class="bg_main">
        <div class="ads">
          <div class="ft_menu clearfix">
            <div></div>
            <div>
              <ul>
                <li><a href="/gdz/ru/algebra">Алгебра</a></li>
                <li><a href="/gdz/ru/biologiya">Биология</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def euroki_pages_html() -> str:
    return """
    <html>
    <body>
      <div class="content one_page book-page">
        <div class="book-navigation__panel gdz_view">
          <a href="/gdz/ru/biologiya/2_klass/book-1/task-1">1</a>
          <a href="/gdz/ru/biologiya/2_klass/book-1/task-2">2</a>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def euroki_solution_html() -> str:
    return """
    <html>
    <body>
      <div id="txt_cont">
        <img class="new_label lozad" src="data:image/png;base64,AAA" data-src="https://www.euroki.org/assets/new.png" alt="new" />
        <img class="gdz_image" src="data:image/png;base64,AAA" data-src="https://imgs.euroki.org/books/gdzs/4889/1693890.png" alt="Решение 1" />
      </div>
    </body>
    </html>
    """


@pytest.fixture
def megaresheba_main_html() -> str:
    return """
    <html>
    <body>
      <div>
        <div>
          <main>
            <div class="mainMenu desktopMenu">
              <ul>
                <li>
                  <a href="/class-1">1 класс</a>
                  <a href="/publ/gdz/matematika/1_klass/1">Математика</a>
                </li>
              </ul>
            </div>
            <div class="content">
              <ul class="indexTable">
                <li>
                  <div>
                    <a href="/index/001/0-4">Математика</a>
                  </div>
                </li>
              </ul>
            </div>
          </main>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def megaresheba_pages_html() -> str:
    return """
    <html>
    <body>
      <div id="tasks">
        <div>
          <div>
            <a href="/index/08/0-173/1"><span>1</span></a>
            <a href="/index/08/0-173/2"><span>2</span></a>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def megaresheba_solution_html() -> str:
    return """
    <html>
    <body>
      <div id="task">
        <div>
          <div>
            <img src="/attachments/images/tasks/000/sample.jpg" alt="Решение" />
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def raketa_html() -> str:
    return """
    <html>
    <body>
      <a href="/matematika/1-klass/">1</a>
      <a href="/matematika/1-klass/moro-uchebnik/">Учебник Моро</a>
      <a href="/matematika/1-klass/moro-uchebnik/nomer-1/">Номер 1</a>
      <div class="description">
        <p>Номер 1. Ответ: 1, 2, 3, 4</p>
      </div>
      <img src="/images/solution.png" alt="Решение" />
    </body>
    </html>
    """


@pytest.fixture
def reshak_html() -> str:
    return """
    <html>
    <body>
      <a href="/tag/5klass_math.html">Математика</a>
      <a href="/reshebniki/matematika/5/merzlyak/index.html">Мерзляк 5 класс</a>
      <a href="/otvet/reshebniki.php?otvet=1&predmet=merzlyak5">1</a>
      <div class="pic_otvet1">
        <img src="/reshebniki/matematika/5/merzlyak/images1/1.png" alt="Ответ 1" />
      </div>
    </body>
    </html>
    """


@pytest.fixture
def pomogalka_html() -> str:
    return """
    <html>
    <body>
      <a href="/1-klass/">1 класс</a>
      <a href="/1-klass/matematika/">Математика</a>
      <a href="/1-klass/matematika/moro/">Моро 1 класс</a>
      <a href="/1-klass/matematika/moro/stranica-h1-4/">Страница 4</a>
      <div class="task-txt">
        <img src="/img-res/1-klass-moro-2025/h1-4_1.png" alt="Решение" />
      </div>
    </body>
    </html>
    """


@pytest.fixture
def putina_html() -> str:
    return """
    <html>
    <body>
      <a href="/klass-1">1 класс</a>
      <a href="/klass-1/matematika">Математика</a>
      <a href="/klass-1/matematika/moro">Учебник Моро</a>
      <div class="tasks" data-url="/klass-1/matematika/moro">
        <a href="#task?t=1-p-4">4</a>
      </div>
    </body>
    </html>
    """


@pytest.fixture
def putina_json() -> str:
    return """{"success": true, "editions": [{"title": "Учебник", "images": [{"title": "Решение 4", "url": "/attachments/images/tasks/000/094/573/0002/sample.jpg"}]}]}"""


@pytest.fixture
def ltd_html() -> str:
    return """
    <html>
    <body>
      <a href="/1-class/">1</a>
      <a href="/1-class/matematika/">Математика</a>
      <a href="/1-class/matematika/moro/">Моро 1 класс</a>
      <div class="variants">
        <a class="image_load" img="/content/1-class/matematika/moro/exercise/1/2">2</a>
      </div>
    </body>
    </html>
    """
