# Domain-driven design, Hexagonal architecture of ports and adapters, Dependency injection и Python

\- Глянь, статью на Хабр подготовил.
\- Эм... а почему заголовок на английском?
\- Предметно-ориентированное проектирование, Гексагональная архитектура портов и адаптеров, Внедрение зависимостей и Пайтон?
С пронзительным хлопком в воздухе материализуется обалдевший Сатана в обличии сине-жёлтого питона...

---

Полтора года назад я расстался с миром Python/Django и попал в мир
Kotlin/Spring Boot и чистой архитектуры.
Недавно нам понадобилось написать небольшую программу для внутренних
целей. Недолго заморачиваясь, я написал её на всё ещё любимом
Python. К моему удивлению и удовольствию, её удалось
написать примения вышеупомянутые практики
Предметно-ориентированного проектирования (Domain-driven design, DDD),
Чистой Архитектуры (Clean architecture) и
Внедрения зависимостей (Dependency Injection, DI).

Представляю на ваш суд технический рассказ о том, что такое
и как связаны между собой все вышеупомянутые темы.


## Prologue

Полтора года назад я сменил место работы и расставшись с миром Python/Django
и окунулся в мир Kotlin/Spring Boot.
Компания Abloy собирала команду для своего технологического авангарда.
Мы должны были помочь перенести её из прошлой механической
эры в эру цифрового будущего. Желание "делать качественно" поддерживалось на
всех уровнях менеджмента. Mы могли *творить* с чистого листа.

Муки выбора стека для бэкэнда были короткими:
двое джавистов против одного питониста не оставили места для манёвра.
Spring Boot в качестве фреймворка был выбран по той же причине.
В первые же дни работы мы попробовали Kotlin и к Java больше не возвращались.
Дальше пошло по накатаной: архитектура - ну а что мудрить, MVC.
Сделаем традиционные слои: бизнес-слой, контроллеры, персистентность...

**СТОП!**

Опять за старое?
Давайте потратим время на понимание предметной области.
Распишем истории пользователей (*User Story Mapping*).
Вникнем в практики DDD.
В конце концов почитаем, что умные люди говорят о надёжных архитектурных
решениях.

Прошло полтора года. Наше приложение стремительно растёт и усложняется.
Несмотря на это, его легко поддерживать, тестировать и развивать -
всё благодаря качественному фундаменту и архитектуре.
Код получается выразительным и легковесным. Компоненты - легко заменяемыми.
Во всех отношениях это приложение качественнее всего написанного
нами в прошлом.

Недавно нашим железячникам понадобился CI-компонент для сборки, шифрования и
и выкладывания прошивок электронных замков на сервер.
Я вызвался помочь с написанием, т.к. ребята немного знакомы с Python
(а основным рабочим инструментом у них служит bare-metal C).
Даже в таком маленьком приложении нам удалось
применить лучшие практики DDD и Чистой архитектуры.
Оглядываясь назад понимаю какие пробелы в моём опыте не позволяли
писать и решать задачи бизнеса *так* элегантно.
И если что-то из вышеперечисленнго вам не знакомо, прошу!


## Dependency Injection

Вы знаете что такое Внедрение зависимости ака Dependency Injection (DI).
Точно знаете, хотя можете и не вспомнить формальное определение.
Давайте на небольшом примере вспомним, в чём плюсы и минусы этого подхода
(если вам угодно - шаблона).

Допустим нам понадобилась функция, отправляющая сообщения с пометкой "ТРЕВОГА!"
в шину сообщений. После недолгих размышлений напишем:

```python
from my_cool_messaging_library import get_message_bus()

def send_alert(message: str):
    message_bus = get_message_bus()
    message_bus.send(topic='alert', message=message)
```

В чём главная проблема функции `send_alert()`?
Она зависит от объекта `message_bus`, но для вызывающего эта зависимость
совершенно не очевидна! А если вы хотите отправить сообщение
по другой шине? А как насчёт уровня магии, необходимой
чтобы это протестировать? Что, что? `mock.patch(...)` говорите?
Коллеги, атака в лоб провалилась, давайте зайдём с флангов.

```python

  from my_cool_messaging_library import MessageBus

  def send_alert(message_bus: MessageBus, message: str):
      message_bus.send(topic='alert', message=message)
```

Казалось - небольшое изменение, добавили аргумент в функцию.
Но одним лишь этим изменением мы убиваем нескольких зайцев:
Вызывающему очевидно, что функция `send_alert()` **зависит**
от объекта `message_bus` типа `MessageBus` (да здравствуют аннотации!).
А тестирование, из обезьяньих патчей с бубном, превращается
в написание краткого и ясного кода. Не верите?

```python

def test_send_alert_sends_message_to_alert_topic()
    message_bus_mock = MessageBusMock()
    send_alert(message_bus_mock, "A week of astrology at Habrahabr!")

    assert message_bus_mock.sent_to_topic == 'alert'
    assert message_bus_mock.sent_message == "A week of astrology at Habrahabr!"

class MessageBusMock(MessageBus):
    def send(self, topic, message):
        self.sent_to_topic = topic
        self.sent_message = message
```

Тут искушённый читатель задастся вопросом: неужели
придётся передавать экземпляр `message_bus` в функцию `send_alert()`
при каждом вызове? Но ведь это неудобно! В чём смысл каждый раз
писать

```python
send_alert(get_message_bus(), "Stackoverflow is down")
```

Попытаемся решить эту проблему посредством ООП:

```python

class AlertDispatcher:
    _message_bus: MessageBus

    def __init__(self, message_bus: MessageBus):
        self._message_bus = message_bus

    def send(message: str):
        self._message_bus.send(topic='alert', message=message)

alert_dispatcher = AlertDispatcher(get_message_bus())
alert_dispatcher.send("Oh no, yet another dependency!")
```

Теперь уже класс `AlertDispatcher` **зависит** от объекта типа `MessageBus`.
Мы **внедряем** эту зависимость в момент создания объекта `AlertDispatcher`
посредством передачи зависимости в метод `__init__()`. Мы связали
(we have wired, не путать с coupling!) объект и его зависимость.

Но теперь акцент смещается с `message_bus` на `alert_dispatcher`!
Этот **компонент** может понадобиться в различных местах приложения.
Мало ли откуда нужно оправить сигнал тревоги!
Значит, необходим некий глобальный контекст из которого можно
будет этот объект достать.
Но прежде чем перейти к построению такого контекста, давайте
немного порассуждаем о компонентах и их связывании.

## Componential architecture

Говоря о внедрении зависимостей мы не сильно заостряли внимание
на типах. Но вы наверняка догадались, что `MessageBus` - это всего
лишь абстракция, интерфейс, или как бы сказал PEP-544 - протокол.
Где-то в нашем приложении объявленo:

```python
class MessageBus(typing.Protocol):
    def send(topic: str, message: str):
        pass
```

В проекте также есть простейшая имплементация `MessageBus`-a,
записывающая сообщения в список.

```python
class MemoryMessageBus(MessageBus):
    messages = []

    def send(topic: str, messagge: str):
        self.messages.append((str, message))
```

Таким же образом можно абстрагировать бизнес-логику, разделив абстрактный
сценарий пользования (use case) и его имплементацию:

```python
class DispatchAlertUseCase(typing.Protocol):
    def dispatch_alert(message: str):
        pass
```

```python
class AlertDispatcherService(DispatchAlertUseCase):
    _message_bus: MessageBus

    def __init__(self, message_bus: MessageBus):
        self._message_bus = message_bus

    def dispatch_alert(message: str):
        self._message_bus.send(topic='alert', message=message)
```

Давайте для наглядности добавим HTTP-контроллер, который
принимает сообщения по HTTP-каналу и вызывает `DispatchAlertUseCase`:

```python
class ChatOpsController:
    ...
    def __init__(self, dispatch_alert_use_case: DispatchAlertUseCase):
        self._dispatch_alert_use_case = dispatch_alert_use_case

    @post('/alert)
    def alert(self, message: Message):
        self._dispatch_alert_use_case.dispatch_alert(message)
        return HTTP_ACCEPTED
```

Наконец, всё это необходимо связать воедино:

```python
from my_favourite_http_framework import http_server

def main():
    message_bus = MemoryMessageBus()
    alert_dispatcher_service = AlertDispatcherService(message_bus)
    chat_opts_controller = ChatOpsController(alert_dispatcher_service)

    http_server.start()
```

Первой же реакцией здорового программиста будет
"ну нафига громоздить столько кода?".
Ваша правда, всё вышенаписанное умещается в одну коретенькую функцию:

```python
@post('/alert)
def alert(message: Message):
    bus = MemoryMessageBus()
    bus.send(topic='alert', message=message)
    return HTTP_ACCEPTED
```

Коротко? Ещё как! Маштабируемо? Вообще никак. Почему? Из-за
сильнейшей связанности компонентов (coupling) в коде.
Уместив всё в одну функцию таким образом,
мы намертво привязали логику отправки оповещений к конретной реализации
шины сообщений. Но это ещё пол-беды. Самое ужасное то, что
**бизнес-составляющая полностью растворилась в технических деталях**.
Не поймите меня неправильно, подобный код вполне имеет право на
существование. Но простит ли растущее приложение такой сжатый подход?

Давайте же вернёмся к нашей компонентной архитекруте. В чём её
преимущества?

* Компоненты **изолированы** и не зависимы друг от друга напрямую.
  Вместо этого они **связаны посредством абстракций**.
* Каждый компонент работает в чётких рамках и **решает лишь одну задачу**.
* Это значит, что компоненты могут быть протестированы как в полной изоляции, так и в
  любой произвольной комбинации включающей тестовых двойников (test double).
  Думаю не стоит объяснять, насколько проще тестировать изолированные
  части программы. Подход к TDD меняется с "мы пишем тесты" на
  ~~"тесты утром, вечером код"~~ "сначала пишем тест, потом пишем код".
* С учётом того, что зависимости описываются абстракциями, можно
  безболезненно заменить один компонент другим. В нашем примере -
  вместо `MemoryMessageBus` можно бухнуть `DbMessageBus`, да хоть
  в файл на диске писать - тому кто вызывает `message_bus.send(...)`
  нет до этого никакого дела.

"Да это же SOLID!" - скажите вы. И будете абсолютно правы.
Не удивлюсь, если у вас возникло чувство дежа-вю, ведь
благородный дон @zueve совсем недавно
детально описал связь SOLID и Чистой архитекруты
в статье ["Clean Architecture глазами Python-разработчика"](https://habr.com/ru/company/exness/blog/494370/).
И наша компонентная архитектура находится лишь в шаге от
чистой "гексагональной" архитекруты.
Кстати, причём тут гексагон?


## Architecture is about intent

Одно из замечательных высказываний дяди Боба на тему
архитектуры приложений - *Architecture is about intent*
(Намерения - в архитектуре).

Что вы видите на этом скриншоте?

!!!!!
screenshot
!!!!!

Не удивлюсь, если многие ответили "Типичное Django-приложение".
Отлично! А что же делает это приложение? Вы вероятно телепат
80го уровня, если смогли ответить на этот вопрос правильно.
Лично я не именю ни малейшего понятия - это скриншот
первого попавшегося Django-приложения, найденного на
Гитхабе.

Роберт Мартин развивает идею [дальше](https://www.youtube.com/watch?v=WpkDN78P884).
Взгляните на архитектурный план этажа и догадайтесь,
для чего предназначено это здание?


<spoiler title="Разгадка">
Это один из этажей библиотеки Oodi в Хельсинки.
</spoiler>

Надеюсь вам было несложно отгадать эту маленькую загадку
и из неё вы вынесли главное:
архитектура должна встречать нас с порога, буквально
с момента окончания `git clone...`.
Как здорово, когда код прижоения организован
таким образом, что предназначение того или иного компонента
лежит на поверхности!

В "Гексагональной архитекруте", гексагон призван
упростить восприятие архитекруты.
Мудрёно? Пардон, сейчас всё будет
продемонстрировано наглядно.

## Hexagonal architecture of Ports and Adapters

"У нас Гексагональная архитектура портов и адаптеров" -
с этой фразы начинается рассказ об архитектуре приложения
новым членам команды.
Далее мы показываем им такую картинку:

[КАРТИНКА]

Домен (предметная область) - это сердце приложения.
Классы, методы, фунцкии, константы и другие объекты домена повторяют
язык предметной области. Например правило Хабра
> "Пользователь может голосовать за публикации, комментарии и
> карму других пользователей если его карма ≥ 5"
будет отображено именно здесь. И как вы наверняка поняли,
в домене нет места HTTP, SQL, RabbitMQ, AWS и т.д. и т.п.

Зато всему этому празднику технологий есть место в **адаптерах**
подсоединяемых к **портам**. Команды и запросы поступают в приложение
через **ведущие** (driver) или **API** порты.
Команды и запросы которые отдаёт приложение поступают в **ведомые** порты (driven port).
Их также называют портами интерфейса поставщика услуг (Service Provider Interface, SPI).

Mежду портами и доменом сидят дирижёры - **серсивы приложения** (Application services).
Они являются *связующим звеном* между сценариями использования,
доменом и ведомыми портами неободимыми для выполнения сценария.
Также стоит упомянуть, что именно сервис приложения определяет,
будет ли сценарий выполнятся в рамках общей транзакции, или нет.

OFFTOP: Анемичные модели, или Фаулер и Эванс не одобряе.
Со временем мы обнаружили, что некоторые модели в нашем домене - анемичны
и немалая связующая часть бизнес-логики лежит в сервисах приложения.
Советую ознакомится с [переводом](https://habr.com/ru/post/346016/)
(спасибо, @pankraty!) статьи [The Anaemic Domain Model is no Anti-Pattern, it’s a SOLID design](https://blog.inf.ed.ac.uk/sapm/2014/02/04/the-anaemic-domain-model-is-no-anti-pattern-its-a-solid-design/) в которой данная проблема рассмотрена на порядок глубже.

Всё это - и порты, и адаптеры и сервисы приложения и даже домен - **слои**
архитектуры. Главной заповедью взаимодействия между слоями является
"Зависимости всегда направлены от внешних слоёв к центру приложения".
Например, адаптер может ссылаться на домен, но не наоборот.

И... ВСЁ. Это - вся суть Гексагональной архитектуры портов и адаптеров.
Она замечательно подходит для задач с обширной предметной областью.
Для голого CRUDа такая архитектура избыточна - Active Record вам в руки.
Давайте же засучим рукава и разберёмся, как связана
Гексагональная и "компонентная" архитектуры.


## Interlude

Дорогой читатель! Спасибо что дошли до этого места, надеюсь сей опус
не утомил вас, а наоборот оказался познавательным и интересным.

Во второй части вас ждёт реализация гексагональной архитектуры
на знакомом нам всем примере. В первой части мы старались
абстрагироваться от конкретных решений: будь то фреймворки или
библиотеки. Последующий пример построен на основе Django и DRF
с целью продемонстрировать, как можно вплести гексагональную
архитектуру в фреймворк с устоявшимися традициями и архитектурными
решениями.
В приведённых примерах вырезаны некоторые необязательные участки
и имеются допущения. Это сделано для того, чтобы мы могли сфокусироваться
на важном и не отвлекались на второстепенные детали.
Полностью исходный код примера доступен в репозитории
https://github.com/basicWolf/hexagonal-architecture-django.


# Upvote a post at Hubruhubr

Представим, что мы разрабатываем новую платформу
коллективных технических блогов "Хубрухубр".
и нам нужно реализовать сценарий пользования
"Проголосовать за публикацию".
Вместе с командой экспертов мы разобрали некоторые нюансы этого сценария:

Рейтинг публикации меняется путём голосования пользователей.

1. Пользоатель может проголосовать "ЗА" или "ПРОТИВ" публикации.
2. Пользователь может голосовать за публикации если его карма ≥ 5.
3. Проголосовать можно лишь один раз, изменить голос нельзя.

Переводя на язык архитекруты - в наше приложение
нужно добавить ведущий порт CastArticleVotingtUseCase`, который
принимает ID пользователя, ID публикации и значение голоса: за или против.

## Driver port: Cast article vote use case

TODO: КАРТИНКА

Итак, первый кусочек реализации сценария - это его абстрактное описание.

```python
# src/myapp/application/ports/api/cast_article_vote/cast_aticle_vote_use_case.py

class CastArticleVoteUseCase(Protocol):
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        raise NotImplementedError()
```

Все входные параметры сценария обёрнуты в единую структуру-команду
`CastArticleVoteCommand` [source](http://todo),
а все возможные результаты объединены
посредством `typing.Union` в `CastArticleVoteResult` [source](http://todo).


```python
# src/myapp/application/ports/api/cast_article_vote/cast_article_vote_command.py

@dataclass
class CastArticleVoteCommand:
    user_id: UUID
    article_id: UUID
    vote: Vote
```

```python
# src/myapp/application/ports/api/cast_article_vote/cast_article_vote_result.py

@dataclass
class InsufficientKarmaResult:
    user_with_insufficient_karma_id: UUID

    def __str__(self) -> str:
        return f'User {self.user_with_insufficient_karma_id} does not have ' \
                'enough karma to cast a vote'
...

CastArticleVoteResult = Union[
    VoteCastResult,
    InsufficientKarmaResult,
    VoteAlreadyCastResult,
]
```

Здесь также появляется необходимость в моделях домена,
`Vote` [source](http://todo) - обозначающей голос: за или против
и `ArticleVote` [source](http://todo) - описывающей голос полностью:
кто, за что и как проголосовал:

```python
# src/myapp/application/domain/model/vote.py

class Vote(Enum):
    UP = 'up'
    DOWN = 'down'
```

```python
# src/myapp/application/domain/model/article_vote.py

@dataclass
class ArticleVote:
    user_id: UUID
    article_id: UUID
    vote: Vote
    id: UUID = field(default_factory=uuid4)
```
</spoiler>

Работа с гексагональной архитектурой чем-то напоминает
прищурившегося Леонардо ди Каприо с фразой "We need to go deeper".
Набросав каркас сценария пользования, можно примкнуть к нему
с двух сторон: имплементировать бизнес-логику сценария
или заняться API адаптерами, которые его вызывают.
Давайте так и поступим - напишем HTTP адаптер с помощью
Django Rest Framework.

### HTTP API Adapter

TODO: КАРТИНКА

Наш HTTP адаптера, или на языке Django и DRF - View, до безобразия
прост. За исключением преобразований запроса и ответа, он уменьшается
в несколько строк (TODO: [source](http://) ):

```python
# src/myapp/application/adapter/api/http/article_vote_view.py

class ArticleVoteView(APIView):
    ...

    def __init__(self, cast_article_vote_use_case: CastArticleVoteUseCase):
        self.cast_article_vote_use_case = cast_article_vote_use_case
        super().__init__()

    def post(self, request: Request) -> Response:
        cast_article_vote_command = self._read_command(request)
        result = self.cast_article_vote_use_case.cast_article_vote(
            cast_article_vote_command
        )
        return self._build_response(result)

    ...
```

И как вы поняли, смысл всего этого сводится к

1. Принять HTTP запрос, десериализовывать и валидировать входные данные.
2. **Запустить сценарий пользования**.
3. Сериализовать и возвратить результат выполненного сценария.

Этот адаптер конечно же строился по кирпичику с пременением практик TDD
и использованием инструментов Django и DRF для тестирования view-шек.
Ведь для теста достаточно построить запрос (request), скормить
его адаптеру и проверить ответ (response). При этом мы полностью контролируем
основную зависимость `cast_article_vote_use_case: CastArticleVoteUseCase`
и можем внедрить на её место тестового двойника.

Например, давайте напишем тест для сценария, в котором пользователь
пытается проголосовать повторно. Ожидаемо, что статус в ответе будет
`409 CONFLICT` (TODO: [source](http://) ):

```python
# tests/test_myapp/application/adapter/api/http/test_article_vote_view.py

def test_post_article_vote_returns_conflict(
    arf: APIRequestFactory,
    user_id: UUID,
    article_id: UUID
):
    # В роли объекта реализующего сценарий выступает
    # специализированный двойник, возвращающий при вызове
    # .cast_article_vote() результат, который будет передан
    # ему в конструкторе
    cast_article_use_case_mock = CastArticleVoteUseCaseMock(
        returned_result=VoteAlreadyCastResult(
            user_id=user_id,
            article_id=article_id
        )
    )

    article_vote_view = ArticleVoteView.as_view(
        cast_article_vote_use_case=cast_article_use_case_mock
    )

    response: Response = article_vote_view(
        arf.post(
            f'/article_vote',
            {
                'user_id': user_id,
                'article_id': article_id,
                'vote': Vote.UP.value
            },
            format='json'
        )
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.data == {
        'status': 409,
        'detail': f"User \"{user_id}\" has already cast a vote for article \"{article_id}\"",
        'title': "Cannot cast a vote"
    }
```

Адаптер получает на вход валидные данные, собирает из них команду и вызывает сценарий.
Oднако вместо продакшн-кода, этот вызов получает двойник, который тут же возвращает
`VoteAlreadyCastResult`. Адаптеру остаётся правильно обработать этот результат и
сформировать `HTTP Response`. Остаётся протестировать, соответствует ли
сформированный ответ и его статус ожидаемым значениям.

После написания тестов и имплементации для остальных случаев входных
и выходных данных, мы получаем отточеный API компонент,
хотя бизнес-логика сценария существует пока лишь на бумаге!


## Domain model

Перед тем как воплощать в жизнь наш сценарий, давайте
ещё раз внимательно прочтём требования и добавим
необходимые модели предметной области (ака домена).
Две модели домена, используемые в интерфейсе сценария, у нас уже есть,
это `Vote` [↑](http://anchor) и `ArticleVote` [↑](http://anchor).
Но вот модели, представляющей "голосующего пользователя" пока нет.


### VotingUser

Итак, пользователь может проголосовать за публиакцию.
Но только если значение его кармы больше 5.
Таким образом для модели голосующего пользователя достаточно
двух полей: идентификатора и кармы. А метод "голосовать"
будет возвращать голос пользователя, либо значение обозначающее,
что кармы для голосования не достаточно.
"A почему бы вместо последнего не викинуть исключение?" - спросите вы.
Но разве это исключительная ситуация? Совсем наоборт - она вполне
ожидаема и описана в сценарии.

```python
# src/myapp/application/domain/model/voting_user.py

MINIMUM_KARMA_REQUIRED_FOR_VOTING = 5

class VotingUser:
    id: UUID
    karma: int

    def cast_vote(self, article_id: UUID, vote: Vote) -> CastVoteResult:
      if self.karma >= MINIMUM_KARMA_REQUIRED_FOR_VOTING:
          return ArticleVote(self.id, article_id, vote)
      else:
          return InsufficientKarma(self.id)
```

Здесь `CastVoteResult` - это

```python
@dataclass
class InsufficientKarma:
    user_id: UUID


CastVoteResult = Union[InsufficientKarma, ArticleVote]
```

Все модели предметной области на месте. Осталось их связать в
имплементации сценария.


## Application service

Как дирижёр упрявляет оркестром исполняющим произведение,
так и сервис приложения управляет доменом и ведомыми портами
для выполнении сценария.


### PostRatingService

С места в карьер погрузимся в имплементацию нашего сценария.
В первом приближении сервис реализующий сценарий выглядит так:

```python
# src/myapp/application/service/post_rating_service.py

class PostRatingService(
    CastArticleVoteUseCase  # имплементируем протокол явным образом
):
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        ...
```

Для минимального функционала нам нужен пользователь способный проголосовать,
в виде модели `VoteCastingUser`.
Тут и появляется первая SPI-зависимость `GetVoteCastingUserPort`
задача которой найти голосующего пользователя по его ID:

```python
class PostRatingService(...):
    _get_vote_casting_user_port: GetVoteCastingUserPort,

    def __init__(
        self,
        get_vote_casting_user_port: GetVoteCastingUserPort,
    ):
        self._get_vote_casting_user_port = get_vote_casting_user_port

    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        vote_casting_user = self._get_vote_casting_user_port.get_vote_casting_user(
            user_id=command.user_id
        )

        # пользователя можно сразу пустить в дело
        cast_vote_result: CastVoteResult = vote_casting_user.cast_vote(
            command.article_id,
            command.vote
        )

        return VoteCastResult(cast_vote_result)

```

Стоит ли приводить и код порта? Разве что приличия ради:

```python
# src/myapp/application/ports/spi/get_vote_casting_user_port.py

class GetVoteCastingUserPort:
    def get_vote_casting_user(self, user_id: UUID) -> VotingUser:
        raise NotImplementedError()
```

Вы конечно понимаете, что за кадром мы сначала пишем тесты, а потом код :)
Как и в предыдущих примерах, роль SPI-адаптеров в тестах сервиса играют
дублёры. Но чтобы удержать сей опус в рамках статьи, позвольте
оставить тесты в виде ссылки на исходник [TODO] и двинуться
дальше.

Как насчёт пользователя с недостаточной для голосования кармой?
```python

```

Начнём с ограничений  (constraints) сценария:
`Проголосовать можно лишь один раз, изменить голос нельзя.`.

```python
class PostRatingService(
    CastArticleVoteUseCase  # имплементируем протокол явным образом
):
    ...
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        # Обратимся в порт ArticleVoteExists чтобы проверить,
        # голосовал ли пользователь за публикацию
        if self._article_vote_exists_port.article_vote_exists(
            user_id=command.user_id,
            article_id=command.article_id
        ):
            return VoteAlreadyCastResult(
                cast_vote_user_id=command.user_id,
                cast_vote_article_id=command.article_id
            )
        ...


    # добавим SPI-зависимость ArticleVoteExistsPort
    article_vote_exists_port: ArticleVoteExistsPort

    def __init__(self, article_vote_exists_port: ArticleVoteExistsPort):
        self._article_vote_exists_port = article_vote_exists_port
```


Пользователь может проголосовать "ЗА" или "ПРОТИВ" публикации.


обозначающие "значение голоса" и "голос пользователя за публикацию".
А вот модели "голосующий пользователя" - нет.

Как вы помните, сущности и концепции предметной области зависят
друг от друга, но не имеют доступа к внешним слоям приложения.


Давайте, перед тем как начинать разработку сценария подумаем,
какие модели предметной области можно обособить и отделить
какие концепции относятся к домену, а

Наш сценарий будет воплощён в жизнь внутри сервиса приложения `PostRatingService`:

```python
class PostRatingService(CastArticleVoteUseCase):
    ...
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        ...
```



Давайте набросаем сервис приложения, который реализует вышеприведённый
сценарий и связывает требуемые для него компоненты. Разработку конечно
же правильнее начинать с тестов, но воспринимать ход мыслей в статье,
как мне кажется, проще в "традиционном" порядке - утром код, вечером тесты:

```python
# src/myapp/application/services/post_rating_service.py
from typing import Union

from myapp.application.port.spi.get_voting_user_port import GetVotingUserPort
from myapp.application.port.spi.user_vote_for_post_exists_port import UserVoteForPostExistsPort
from myapp.application.port.spi.save_user_vote_for_post_port import SaveUserVoteForPostPort

from myapp.application.domain.model.voting_user import VotingUser
from myapp.application.domain.model.exceptions.user_already_voted_for_post import UserAlreadyVotedForPostError

from myapp.infrastructure import transactional


class PostRatingService(VoteForPostUseCase):
    _user_vote_for_post_exists_port: UserVoteForPostExistsPort
    _get_voting_user_port: GetVotingUserPort
    _save_user_vote_for_post_port: SaveUserVoteForPostPort

    # Здесь и далее для краткости опущен метод `__init__()`,
    # через который инициализуются поля-зависимости компонента.

    @transactional
    def vote_for_post(self, user_id: UUID, post_id: UUID, vote: Vote)
        -> Union[UserVoteForPost, UserVoteForPostAlreadyCast]:

        # Если пользователь уже проголосовал, то возвращаем
        # специальное значение:
        if self._user_vote_for_post_exists_port.user_vote_for_post_exists(
            user_id,
            post_id
        ):
            raise UserVoteForPostAlreadyCast(user_id, post_id)

        # Если же полжьзователь не голосовал...

        # Загрузим модель "голосующего пользователя" из БД
        voting_user: VotingUser = self._get_voting_user_port.get_voting_user(user_id)

        # Попробуем проголосовать
        user_vote_for_post = voting_user.cast_vote(post_id, vote)

        # И сохранить голос (в БД)
        self._save_user_vote_for_post_port.save_user_vote_for_post(
            user_vote_for_post
        )

        return user_vote_for_post
```

Очень надеюсь, что вышеприведённый код был лёгок для чтения и понимания.
Ведь иначё всё это не имеет никакого значения!

У сервиса три зависимости:

* `get_user_vote_for_post_port: GetUserVoteForPostPort` - загружает голос
  пользовареля, если такой имеется
* `get_voting_user_port: GetVotingUserPort` - загружает и создаёт модель
  пользователя, с помощью которой можно проголосовать за публикацию
* `save_user_vote_for_post_port: SaveUserVoteForPostPort` - сохраняет
  голос пользователя.

Взаимодействие с ними происходит в методе `vote_for_post()`.
Сервис не имеет ни малейшего понятия, каким образом имплементированы
эти зависимости и какого рода хранилище они используют.
Однако важно показать, что взаимодействие должно выполняться
в рамках одной транзакции. Поэтому метод обрамляется декоратором `transactional`.

В сервисе также выполняются *некоторые* из бизнес-требований
данного сценария, например *"За каждую публикацию пользователь может проголосовать один раз"*.
В то же время требование *Пользователь может голосовать за публикации если его карма ≥ 5* скрыто в доменной модели `VotingUser`.

### Domain model

~~Вот она:~~ Модель `VotingUser` - отличный пример для TDD в рамках архитектуры
портов и адаптеров. Давайте напишем один тест, а остальные попросим додумать
вас, уважаемый читатель.

!!!! OFFTOP: TDD
Мой личный подход к TDD - сначала полностью написать тест, невзирая
на отсутствие классов, методов и т.д. Убедиться, что тест
легко читается и обладает другими качествами упомянутыми
Кентом Бэком в [Test Desiderada](https://medium.com/@kentbeck_7670/test-desiderata-94150638a4b3).
И уже потом разбираться с ошибками компиляции и теста.

```python

# test/myapp/application/domain/model/test_voting_user.py

from uuid import uuid4

from myapp.application.domain.model.vote import Vote
from myapp.application.domain.model.voting_user import VotingUser, InsufficientKarmaError

def test_user_with_karma_smaller_than_5_cannot_cast_vote():
    voting_user = VotingUser(karma=4)

    # `VotingUser.cast_vote()` выкидывает исключение,
    # если кармы пользователя не достаточно для голосования
    with pytest.raises(InsufficientKarmaError):
        voting_user.cast_vote(uuid4(), Vote.UP)
```

А вот и модель, которая проходит вышеприведённый тест.
Заметьте, что код компонентов и тестов лежат в файлах с практически
идентичными путямии. Разница лишь в директориях верхнего уровня: `src/` и `test/`.

```python
# src/myapp/application/domain/model/voting_user.py

from uuid import uuid4, UUID

from .vote import Vote

MINIMAL_KARMA_FOR_VOTE = 5

class VotingUser:
    _id: UUID
    _karma: int

    def __init__(self, id: UUID, karma: int):
        self._id = id
        self._karma = karma

    def cast_vote(self, post_id: UUID, vote: Vote):
        if self._karma < MINIMAL_KARMA_FOR_VOTE:
            raise InsufficientKarmaError(
                `User [{self._id}] does not have enough karma to vote`
            )

        return UserVoteForPost(
            id=uuid4(),
            user_id=self._id,
            post_id=post_id,
            vote=vote
        )

class InsufficientKarmaError(Exception):
    ...
```

SPI Ports and Adapters
======================

Работа с гексагональной архитектурой чем-то напоминает знаменитый
мем "We need to go deeper".
Набросав код сервиса и даже написав код домена, можно было позабыть
о том, что в приложении пока нет ни требуемых SPI-портов ни адаптеров.
Нужно дальше углубляться в цепочку вызовов и достраивать необходимые
компоненты.

Давайте рассмотрим SPI-порты и адаптеры на примере ``GetUserVoteForPostPort``:

```python

# src/myapp/application/port/spi/get_user_vote_for_post_port.py

from uuid import UUID
from typing import Protocol

from myapp.application.domain.model.user_vote_for_post import UserVoteForPost

  class GetUserVoteForPostPort(Protocol):
    def get_user_vote_for_post(user_id: UUID, post_id: UUID): UserVoteForPost
        pass
```

Стоит обратить внимание, что один адаптер может имплементировать несколько
портов. Например, имеет смысл сгруппировать операции на определённой
сущности базы данных в одном и том же адаптере.

```python

from myapp.application.adapter.db.entities.user_vote_for_post_entity import UserVoteForPostEntity

class PostVoteDatabaseOperations(GetUserVoteForPostPort):
    def get_user_vote_for_post(user_id: UUID, post_id: UUID) -> UserVoteForPost:
        return UserVoteForPostEntity.objects.get_or_none(
            user_id=user_id,
            post_id=post_id
        )

```


Чуть позже мы поговорим о сервисе приложения, который имплементирует этот порт.
А пока напишем REST-адаптер который будет запускать данный сценарий.

```python
# src/myapp/application/adapter/rest/post_controller.py

from some_http_framework import post

from myapp.application.ports.api.vote_for_post_use_case import VoteForPostUseCase

class BasketItemController:
    vote_for_post_use_case: VoteForPostUseCase

    def __init__(self, vote_for_post_use_case: VoteForPostUseCase)
        self._vote_for_post_use_case = vote_for_post_use_case

    @post('/post/{post_id}/rating/vote')
    def vote_for_post(self, user_id: UUID, post_id: UUID, vote: PostRatingVoteDto):
        rating = self._vote_for_post_use_case(
            user_id,
            post_id,
            PostRatingVote(vote)
        )

        return Response(
            status=HTTP_CREATED,
            content=PostRatingVoteCastResultDto(rating)
        )

```

У этого адаптера чёткие обязанности:

1. Принимать определённые HTTP запросы.
2. [Десериализовывать и валидировать входные данные.]
3. Запустить свенарий пользования `AddItemToBasketUseCase`.
4. [Сериализовать] и возвращать результат выполненного сценария.
5. [А также обрабатывать исключения.]

!!!!!!!!!
Explain DTO!
В приведённом примере за нас это делает некая http-библиотека или
фреймворк. Она превращает входной JSON-поток в дата-класс
`BasketItemDto` и валидирует значения а-ля `Serializer` из
DjangoRestFramework.

Одно из допущений в вышеприведённом коде - это `user_id`. Значение
этого парамаетра может быть взято из JWT-токена, из данных сессии
и т.д. - в данном контексте это не важно.


Уже на этом этапе мы могли бы применить практики TDD и
начать с написания теста и по ходу действия - контроллера.
"Позвольте, а как же `AddItemToBasketUseCase`? -
спросите вы. Очень просто. Это же абстракция! Её конкретной
имплементацией может быть тестовый двойник, например на основе
`MagicMock`, или ещё лучше специализированный, заточенный под
нужды теста.
Давайте для простоты договоримся, что приложение выполняется
в некоем контексте `app_context` с которым может взаимодействовать
тестовый HTTP клиент. Оба объекта передаются в `pytest`-тест.

!!!! как fixture (фикстуры?)

```python
# test/adapter/rest/test_basket_item_controller.py

def test_add_item_to_basket(app_context: AppContext, http_client: TestHttpClient):
    add_item_to_basket_use_case_mock  = MagicMock()
    add_item_to_basket_use_case_mock.add_item_to_basket = MagicMock(
        return_value = UUID('245c8e37-95bb-4a01-be45-38f72550698d')
    )

    app_context.add_controller(
        BasketItemController(add_item_to_basket_use_case_mock)
    )

    response = http_client.post(
        f'/basket/{uuid4()}/items',
        {
            'product_id': uuid4(),
            'count': 1
        }
    )

    assert response.status_code == HTTP_CREATED
    assert response.content == json.serialize(
        BasketItemCreatedResponseDto(
            basket_item_id=UUID('245c8e37-95bb-4a01-be45-38f72550698d')
        )
    }

```

Заметьте, насколько *облегчённее* становится тестирование, когда
нам не нужно загружать всё приложение целиком. Адепты Django
вспомнят о легковесном тестировании вьюшек посредством `RequestFactory`.
Но гексагональная архитектура позволяет шагнуть дальше.
Мы избавились от обезьяних патчей и mock-обёрток конкретных классов.
Мы можем идеально контролировать поведение зависимостей контроллера
благодаря взаимодействию с ними через абстрактный интерфейс.
И тест и контроллер легко модифицировать и отлаживать.


Здесь `BasketItem` - это доменная модель (Domain Model).


## Inversion of Control Containers

A как управлять этим зоопарком, когда
приложение начнёт разрастаться до неприличных размеров?
И тут на помощь приходят Kонтейнеры инверсии управления
(Inversion of Control Containers, IoC-containers).


IoC-container - это фреймворк управляющий объектами и их
зависимостями во время исполнения программы.

Spring был первым _универсальным_ IoC-контейнером / фреймворком
с которым я столкнулся на практике.
Чего уж таить, я не сразу проникся заложенными в него идеями.
По-настоящему ощутить всю мощь автоматического связывания
(autowiring) и сопутствующего функционала я смог лишь когда
приложение начали престраивать в соответствии с практиками чистой архитектуры.
Но об этом чуточку попозже.

Давайте-ка приведём несколько примеров-аналогов на Питоне
для тех, кто не знаком со Springом.

Для начала поможем *условному* Springу понять, какие классы приложения
отданы ему на откуп.
Декораторы для этих целей подойдут как нельзя лучше:

```python
@component
class AlertDispatcher:
    _message_bus: MessageBus

    def __init__(self, message_bus: MessageBus):
        self._message_bus = message_bus
```

Заметим, что `MessageBus` - это всего лишь абстракция, интерфейс, или как бы
сказал PEP-544 - протокол. Т.е. где-то в нашем приложении объявленo:

```python
from abc import ABC, abstractmethod

class MessageBus(ABC):
    @abstractmethod
    def send(topic: str, message: str):
        ...
```

Далее, в проекте также есть простейшая имплементация `MessageBus`-a:

```python
@component
class MemoryMessageBus(MessageBus):
    messages = []

    def send(topic: str, messagge: str):
        self.messages.append((str, message))
```

Заметьте, что `MemoryMessageBus` - это тоже компонент заданый явным образом.
Но в отличии от `AlertDispatcher` у него нет никаких зависимостей.

Сейчас начнётся самое интересное. На старте `Spring` просканирует
приложение и найдёт все классы помеченные как компоненты.
Spring составит граф зависимостей, удостоверится в его корректности,
а потом начнёт создавать объекты в соответствии с этим графом.
В графе имеется компонент `MessageDispatcher` зависящий
от абстракции `MessageBus`. А также есть компонент `MemoryMessageBus`,
который эту абстракцию воплощает. Spring свяжет их автоматически
внедрив экземпляр последнего в конструктор первого.
Т.е. за кулисами выполнит:

```python
context.message_bus = MemoryMessageBus()
context.alert_dispatcher = AlertDispatcher(context.message_bus)
```

А теперь представьте, что у нас есть компонент через который в
приложение поступают данные. Пусть это будет приёмник HTTP запросов,
получающий сообщения в JSON-формате и оповещающий нас
при необходимости:

```python
@component
class ChatOpsController:
    ...
    def __init__(self, alert_dispatcher: AlertDispatcher):
        self._alert_dispatcher = alert_dispatcher

    @post('/alert)
    def alert(self, message: Message):
        self._alert_dispatcher(message)
        return HTTP_ACCEPTED
```






### Телевизор

Вы когда-нибудь пользовались телевизором?
"Аффтар, ты где берёшь такую забористую траву?" - подумало большинство читателей.
Прошу прощения за примитивизм. Телек отлично подходит
для объяснения основных принципов гексагональной архитекруты.
Обещаю, что в следующем же разделе мы вернёмся к коду.
Хотя, в качестве примера можно было бы рассмотреть и телегу с лошадью :)

Представим, что телевизор - это приложение построенное по правилам
гексагональной архитектуры. Вечереет, мы готовимся к просмотру любимого
сериала и первым делом необходимо выполнить простейший сценарий пользования - включить телевизор.
"Да не ворпос - нажал кнопку на пульте".
Окей, а если в пульте сели батарейки?
"Ну... на телеке обычно есть кнопка включения. А вообще у меня Smart-TV, и я им по вай-фаю управляю!"

Итак, мы имеем:
* *Включить телевизор* - *абстрактный* сценарий пользования телевизором.
  На языке нашей архитектуры - это **ведущий (API) порт**, принимающий команду управления приложением.
* *ИК пульт управления*, *Кнопочка на корпусе* и *Виртуальный пульт на смартфоне, передающий команды по WiFi*.
  - методы запуска вышеприведённого сценария,
  а на языке нашей архитектуры - **API адаптеры**, посылающие команды в порт "Включить телевизор".
* Внутри телевизора есть плата, связывающая компоненты, необходимые для включения и выключения телевизора.
  Мы называем её **сервисом приложения**.
* Плата проводит команды от **портов API** к необходимым логическими блокам - **домену**, и связывает выходы
  **домен** с **ведомыми (SPI) портами**: *вывести картинку*, *установить якость*,
   *подать звук* и т.д.
* Физический экран и колонки телевизора - это **SPI адаптеры**.

Надеюсь вам стало чуточку понятнее. Воплотим же всё это в коде!


* https://github.com/basicWolf/hexagonal-architecture-django
