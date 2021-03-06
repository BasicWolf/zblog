# Domain-driven design, Hexagonal architecture of ports and adapters, Dependency injection и Python


## Prologue

\- Глянь, статью на Хабр подготовил.
\- Эм... а почему заголовок на английском?
\- "Предметно-ориентированное проектирование, Гексагональная архитектура портов и адаптеров, Внедрение зависимостей и Пайто..."
С пронзительным хлопком в воздухе материализуется обалдевший Сатана в обличии сине-жёлтого питона.

## Intro

Как же летит время! Два года назад я расстался с миром Django
и очутился в мире Kotlin, Java и Spring Boot.
Это был самый настоящий культурный шок.
Голова гудела от объёма новых знаний.
Xотелось бежать обратно в тёплую, ламповую, знакомую до байтов экосистему Питона.
Особенно тяжело на первых порах мне давалась концепция
инверсии управления (Inversion of Control, IoC) при связывании компонентов.
После прямолинейного подхода Django,
автоматическое внедрение зависимостей
(Dependency Injection, DI) казалось чёрной магией.
Но именно эта особенность фреймворка Spring Boot
позволила проектировать приложения следуя заветам
Чистой Архитектуры.
Самым же большим вызовом стал отказ от философии
"пилим фичи из трекера" в пользу
Предметно-ориентированного проектирования
(Domain-Driven Design, DDD).

Наш проект стремительно растёт и усложняется.
Несмотря на это, его легко поддерживать, тестировать и развивать -
всё благодаря качественному фундаменту и архитектуре.
Код получается выразительным и легковесным. Компоненты - легко заменяемыми.
Во всех отношениях это приложение качественнее всего написанного
каждым членом нашей команды в прошлом.

Оглядываясь назад вспоминаю, какие пробелы в моём опыте и знаниях
не позволяли писать и решать задачи бизнеса *так* элегантно.
Если вы живёте в экоситеме Питона и на практике хотите познакомиться
со всем перечисленным в заголовке, прошу!

Пользуясь случаем, хочу передать благодарность коллегам,
которые поддерживали, учили и направляли меня все эти годы.

## Dependency Injection

Вы знаете что такое Внедрение зависимостей ака Dependency Injection (DI).
Точно знаете, хотя можете и не вспомнить формального определения.
Давайте на небольшом примере рассмотрим, в чём плюсы и минусы этого подхода
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
для тестирования этой функции? Что, что? `mock.patch(...)` говорите?
Коллеги, атака в лоб провалилась, давайте зайдём с флангов.

```python

def send_alert(message_bus: MessageBus, message: str):
    message_bus.send(topic='alert', message=message)
```

Казалось, небольшое изменение, добавили аргумент в функцию.
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
ne    def send(self, topic, message):
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
посредством передачи зависимости в конструктор. Мы связали
(we have wired, не путать с coupling!) объект и его зависимость.

Но теперь акцент смещается с `message_bus` на `alert_dispatcher`!
Этот **компонент** может понадобиться в различных местах приложения.
Мало ли откуда нужно оправить сигнал тревоги!
Значит, необходим некий глобальный контекст из которого можно
будет этот объект достать.
И прежде чем перейти к построению такого контекста, давайте
немного порассуждаем о природе компонентов и их связывании.

## Componential architecture

Говоря о внедрении зависимостей мы не сильно заостряли внимание
на типах. Но вы наверняка догадались, что `MessageBus` - это всего
лишь абстракция, интерфейс, или как бы сказал
[PEP-544](https://www.python.org/dev/peps/pep-0544/) - протокол.
Где-то в нашем приложении объявленo:

```python
class MessageBus(typing.Protocol):
    def send(topic: str, message: str):
        pass
```

В проекте также есть простейшая реализация `MessageBus`-a,
записывающая сообщения в список:

```python
class MemoryMessageBus(MessageBus):
    sent_messages = []

    def send(topic: str, messagge: str):
        self.sent_messages.append((str, message))
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

Первой же реакцией здорового программиста будет:
"ну нафига громоздить столько кода?".
Ваша правда, всё вышенаписанное умещается в одну коротенькую функцию:

```python
@post('/alert)
def alert(message: Message):
    bus = MemoryMessageBus()
    bus.send(topic='alert', message=message)
    return HTTP_ACCEPTED
```

Коротко? Ещё как! Поддерживаемо? Вообще никак. Почему? Из-за
сильнейшей связанности (coupling) компонентов в коде.
Уместив всё в одну функцию таким образом,
мы намертво привязали логику отправки оповещений к конкретной реализации
шины сообщений. Но это ещё полбеды. Самое ужасное то, что
**бизнес-составляющая полностью растворилась в технических деталях**.
Не поймите меня неправильно, подобный код вполне имеет право на
существование. Но простит ли растущее приложение такой сжатый подход?

Вернёмся к нашей компонентной архитектуре. В чём её
преимущества?

* Компоненты **изолированы** и независимы друг от друга напрямую.
  Вместо этого они **связаны посредством абстракций**.
* Каждый компонент работает в чётких рамках и **решает лишь одну задачу**.
* Это значит, что компоненты могут быть протестированы как в полной изоляции, так и в
  любой произвольной комбинации включающей тестовых двойников (test double).
  Думаю не стоит объяснять, насколько проще тестировать изолированные
  части программы. Подход к TDD меняется с невнятного
  "нуууу, у нас есть тесты" на бодрое "тесты утром, вечером код".
* С учётом того, что зависимости описываются абстракциями, можно
  безболезненно заменить один компонент другим. В нашем примере -
  вместо `MemoryMessageBus` можно бухнуть `DbMessageBus`, да хоть
  в файл на диске писать - тому кто вызывает `message_bus.send(...)`
  нет до этого никакого дела.

"Да это же SOLID!" - скажите вы. И будете абсолютно правы.
Не удивлюсь, если у вас возникло чувство дежавю, ведь
благородный дон @zueve год назад
детально описал связь SOLID и Чистой архитектуры
в статье ["Clean Architecture глазами Python-разработчика"](https://habr.com/ru/company/exness/blog/494370/).
И наша компонентная архитектура находится лишь в шаге от
чистой "гексагональной" архитекруты.
Кстати, причём тут гексагон?


## Architecture is about intent

Одно из замечательных высказываний дядюшки Боба на тему
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
первого попавшегося Django-приложения с Гитхаба.

Роберт Мартин развивает идею [дальше](https://www.youtube.com/watch?v=WpkDN78P884).
Взгляните на архитектурный план этажа и догадайтесь,
для чего предназначено это здание?

TODO

<spoiler title="Разгадка">
Это один из этажей библиотеки Oodi в Хельсинки.
</spoiler>

Надеюсь вам было несложно отгадать эту маленькую загадку
и вы вынесли из неё главное:
архитектура должна встречать нас с порога, буквально
с момента окончания `git clone...`.
Как здорово, когда код приложения организован
таким образом, что предназначение того или иного файла,
или директории лежит на поверхности!

В "Гексагональной архитектуре", гексагон в частности
призван упростить восприятие архитектуры.
Мудрено? Пардон, сейчас всё будет
продемонстрировано наглядно.

## Hexagonal architecture of Ports and Adapters

"У нас Гексагональная архитектура портов и адаптеров" -
с этой фразы начинается рассказ об архитектуре приложения
новым членам команды.
Далее мы показываем нечто Ктулхуподобное:

[КАРТИНКА]

Изобретатель термина "Гексагональная архитектура" Алистар Кокбёрн (Alistair Cockburn)
объясняя выбор названия акцентировал внимание на его графическом представлении:

> В гексагоне количество граней не играет роли. Важна сама возможность пририсовать
> порты и адаптеры по необходимости, выходя за рамки изображения послойных однонаправленных графов.
> Термин "гексагональная архитектура" вытекает из визуальной составляющей [2].

Итак, на ~~картине~~ изображении мы видим:

**Домен** (предметная область) - это сердце приложения.
Классы, методы, функции, константы и другие объекты домена повторяют
язык предметной области. Например, правило Хабра
> "Пользователь может голосовать за публикации, комментарии и
> карму других пользователей если его карма ≥ 5"
будет отображено именно здесь. И как вы наверняка поняли,
в домене нет места HTTP, SQL, RabbitMQ, AWS и т.д. и т.п.

Зато всему этому празднику технологий есть место в **адаптерах**
подсоединяемых к **портам**. Команды и запросы поступают в приложение
через **ведущие** (driver) или **API** порты.
Команды и запросы которые отдаёт приложение поступают в **ведомые** порты (driven port).
Их также называют портами интерфейса поставщика услуг (Service Provider Interface, SPI).

Между портами и доменом сидят дирижёры - **сервисы приложения** (Application services).
Они являются *связующим звеном* между сценариями использования,
доменом и ведомыми портами неободимыми для выполнения сценария.
Также стоит упомянуть, что именно сервис приложения определяет,
будет ли сценарий выполнятся в рамках общей транзакции, или нет.

Всё это - и порты, и адаптеры и сервисы приложения и даже домен - **слои**
архитектуры, состоящие из индивидуальных **компонентов**.
Главной заповедью взаимодействия между слоями является
"Зависимости всегда направлены от внешних слоёв к центру приложения".
Например, адаптер может ссылаться на домен или другой адаптер,
а домен ссылаться на адаптер - не может.

И... ВСЁ. Это - вся суть Гексагональной архитектуры портов и адаптеров.
Она замечательно подходит для задач с обширной предметной областью.
Для голого CRUDа а-ля HTTP интерфейс для базы данных,
такая архитектура избыточна - Active Record вам в руки.

Давайте же засучим рукава и разберём на примере,
как спроектировать Django-приложение по канонам
гексагональной архитектуры.

## Interlude

Дорогой читатель! Спасибо, что дошли до этого места, надеюсь сей опус
не утомляет вас, а наоборот захватывает и открывает новые горизонты.

Во второй части вас ждёт реализация гексагональной архитектуры
на знакомом нам всем примере. В первой части мы старались
абстрагироваться от конкретных решений, будь то фреймворки или
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
2. Пользователь может голосовать если его карма ≥ 5.
3. Проголосовать за данную публикацию можно лишь один раз, изменить голос нельзя.

С чего же начать работу? Конечно же с построения модели предметной области!

## Domain model

Давайте ещё раз внимательно прочтём требования и подумаем,
как описать "пользователя голосующего за публикацию"?
Например ([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/domain/model/voting_user.py)):

```python
# src/myapp/application/domain/model/voting_user.py

class VotingUser:
    id: UUID
    voting_for_article_id: UUID
    voted: bool
    karma: int

    def cast_vote(self, vote: Vote) -> CastArticleVoteResult:
        ...
```

На первый взгляд - сомнительного вида творение.
Но обратившись к деталям сценария мы убедимся, что
данный набор данных - необходимый и достаточный для
голосования.
`Vote` и `CastArticleVoteResult` - это также
модели домена
(source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/domain/model/vote.py)):

```python
# src/myapp/application/domain/model/vote.py

# Обозначает голос "За" или "Против"
class Vote(Enum):
    UP = 'up'
    DOWN = 'down'
```

В свою очередь `CastArticleVoteResult` - это тип объединяющий оговорённые исходы
сценария:  `ГолосПользователя`, `НедостаточноКармы`, `ПользовательУжеПроголосовалЗаПубликацию`
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/domain/model/cast_article_vote_result.py#L19)):

```python
# src/myapp/application/domain/model/cast_article_vote_result.py
...
CastArticleVoteResult = Union[ArticleVote, InsufficientKarma, VoteAlreadyCast]
```

Как вы думаете, каких данных достаточно для описания результата
успешно выполненного сценария?

<spoiler title="Ответ">

([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/domain/model/article_vote.py))

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

Но самое интересное будет происходить в теле метода `cast_article_vote()`.
И начнём мы конечно же с тестов.
Первый же тест нацелен на проверку успешно выполненного сценария
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/tests/test_myapp/application/domain/model/test_voting_user.py#L16)):

```python

def test_cast_vote_returns_article_vote(user_id: UUID, article_id: UUID):
    voting_user = VotingUser(
        user_id=user_id,
        voting_for_article_id=article_id,
        karma=10
    )

    result = voting_user.cast_vote(Vote.UP)

    assert isinstance(result, ArticleVote)
    assert result.vote == Vote.UP
    assert result.article_id == article_id
    assert result.user_id == user_id
```

Запускаем тест и... ожидаемый фейл.
В лучших традициях ТДД мы начнём игру в пинг-понг с тестами
и кодом, с каждым тестом дописывая сценарий до полной готовности
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/domain/model/voting_user.py)):

```python
MINIMUM_KARMA_REQUIRED_FOR_VOTING = 5

...

def cast_vote(self, vote: Vote) -> CastArticleVoteResult1:
    if self.voted:
        return VoteAlreadyCast(
            user_id=self.id,
            article_id=self.voting_for_article_id
        )

    if self.karma < MINIMUM_KARMA_REQUIRED_FOR_VOTING:
        return InsufficientKarma(user_id=self.id)

    self.voted = True

    return ArticleVote(
        user_id=self.id,
        article_id=self.voting_for_article_id,
        vote=vote
    )
```

На этом мы закончим моделирование предметной области
и приступим к написанию API приложения.

## Driver port: Cast article vote use case

Как было сказано ранее, в гексагональной архитектуре,
приложение управляется через API-порты.

Чтобы как-то дотянуться до доменной модели, в наше приложение
нужно добавить ведущий порт `CastArticleVotingtUseCase`, который
принимает ID пользователя, ID публикации, значение голоса: за или против
и возвращает результат выполненного сценария
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/ports/api/cast_article_vote/cast_aticle_vote_use_case.py)):

```python
# src/myapp/application/ports/api/cast_article_vote/cast_aticle_vote_use_case.py

class CastArticleVoteUseCase(Protocol):
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        raise NotImplementedError()
```

Все входные параметры сценария обёрнуты в единую структуру-команду
`CastArticleVoteCommand`
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/ports/api/cast_article_vote/cast_article_vote_command.py)),
а все возможные результаты объединены - это уже знакомая модель домена
`CastArticleVoteResult` ([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/domain/model/cast_article_vote_result.py)):

```python
# src/myapp/application/ports/api/cast_article_vote/cast_article_vote_command.py

@dataclass
class CastArticleVoteCommand:
    user_id: UUID
    article_id: UUID
    vote: Vote
```

Работа с гексагональной архитектурой чем-то напоминает
прищурившегося Леонардо ди Каприо с фразой "We need to go deeper".
Набросав каркас сценария пользования, можно примкнуть к нему
с двух сторон.
Можно имплементировать сервис, который свяжет доменную модель
и ведомые порты для выполнения сценария,
или заняться API адаптерами, которые вызывают этот сценарий.
Давайте зайдём со стороны API и напишем HTTP адаптер с помощью
Django Rest Framework.

### HTTP API Adapter

Наш HTTP адаптер, или на языке Django и DRF - `View`, до безобразия
прост. За исключением преобразований запроса и ответа, он умещается
в несколько строк ([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/adapter/api/http/article_vote_view.py)):

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

1. Принять HTTP запрос, десериализировать и валидировать входные данные.
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
`409 CONFLICT` ([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/tests/test_myapp/application/adapter/api/http/test_article_vote_view.py)):

```python
# tests/test_myapp/application/adapter/api/http/test_article_vote_view.py

def test_post_article_vote_with_same_user_and_article_id_twice_returns_conflict(
    arf: APIRequestFactory,
    user_id: UUID,
    article_id: UUID
):
    # В роли объекта реализующего сценарий выступает
    # специализированный двойник, возвращающий при вызове
    # .cast_article_vote() контролируемый результат.
    # Можно и MagicMock, но нужно ли?
    cast_article_use_case_mock = CastArticleVoteUseCaseMock(
        returned_result=VoteAlreadyCast(
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
`VoteAlreadyCast`. Адаптеру же нужно правильно обработать этот результат и
сформировать `HTTP Response`. Остаётся протестировать, соответствует ли
сформированный ответ и его статус ожидаемым значениям.

Ещё раз попрошу заметить, насколько *облегчённее* становится тестирование, когда
не нужно загружать всё приложение целиком. Адепты Django
вспомнят о легковесном тестировании вьюшек посредством `RequestFactory`.
Но гексагональная архитектура позволяет шагнуть дальше.
Мы избавились от обезьяних патчей и mock-обёрток конкретных классов.
Мы легко управляем поведением зависимостей нашего `View`,
ведь взаимодействие с ними происходит через абстрактный интерфейс.
Всё это легко модифицировать и отлаживать.

После написания тестов и имплементации для остальных случаев входных
и выходных данных, мы получаем отточеный API компонент.
Следующим шагом нужно пристыковать этот компонент к рабочей
версии сценария.

## Application services

Как дирижёр упрявляет оркестром исполняющим произведение,
так и сервис приложения управляет доменом и ведомыми портами
для выполнении сценария.


### PostRatingService

С места в карьер погрузимся в имплементацию нашего сценария.
В первом приближении сервис реализующий сценарий выглядит так
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/service/post_rating_service.py)):

```python
# src/myapp/application/service/post_rating_service.py

class PostRatingService(
    CastArticleVoteUseCase  # имплементируем протокол явным образом
):
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        ...
```

Отлично, но откуда возьмётся голосующий пользователь?
Тут и появляется первая SPI-зависимость `GetVotingUserPort`
задача которой найти голосующего пользователя по его ID.
Но как мы помним, доменная модель не занимается записью
голоса в какое-либо долговременное хранилище вроде БД.
Для этого понадобится ещё одна SPI-зависимость `SaveArticleVotePort`:

```python
# src/myapp/application/service/post_rating_service.py

class PostRatingService(
    CastArticleVoteUseCase
):
    _get_voting_user_port: GetVotingUserPort
    _save_article_vote_port: SaveArticleVotePort

    # def __init__(...) # внедрение зависимостей oпустим, чтобы не раздувать листинг

    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        voting_user = self._get_voting_user_port.get_voting_user(
            user_id=command.user_id,
            article_id=command.article_id
        )

        cast_vote_result = voting_user.cast_vote(command.vote)

        if isinstance(cast_vote_result, ArticleVote):
            self._save_article_vote_port.save_article_vote(cast_vote_result)

        return cast_vote_result
```

Вы наверняка представили как выглядят интерфейсы этих SPI-зависимостей
Приведём один из интерфейсов здесь ([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/ports/spi/save_article_vote_port.py)):

```python
# src/myapp/application/ports/spi/save_article_vote_port.py

class SaveArticleVotePort(Protocol):
    def save_article_vote(self, article_vote: ArticleVote) -> ArticleVote:
        raise NotImplementedError()
```

За кадром мы конечно же сначала напишем тесты, а уже потом код :)
При написании юнит-тестов роль SPI-адаптеров в тестах сервиса,
как и в предыдущих примерах, играют дублёры.
Но чтобы удержать сей опус в рамках статьи, позвольте оставить тесты
в виде ссылки на исходник
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/tests/test_myapp/application/service/test_post_rating_service.py))
и двинуться дальше.

## SPI Ports and Adapters

Продолжим рассматривать SPI-порты и адаптеры на примере
``SaveArticleVotePort``. К этому моменту можно было и забыть,
что мы всё ещё надохимдя в рамках Django. Ведь до сих
пор не было написано того, с чего обычно начинается
любое Django-приложение - модель данных!
Тем не менее, не стоит торопиться. Начнём с адаптера,
который можно подключить в вышеуказанный порт
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/adapter/spi/persistence/repository/article_vote_repository.py))

```python
# src/myapp/application/adapter/spi/persistence/repository/article_vote_repository.py

from myapp.application.adapter.spi.persistence.entity.article_vote_entity import (
    ArticleVoteEntity
)
from myapp.application.domain.model.article_vote import ArticleVote
from myapp.application.ports.spi.save_article_vote_port import SaveArticleVotePort


class ArticleVoteRepository(
    SaveArticleVotePort,
):
    def save_article_vote(self, article_vote: ArticleVote) -> ArticleVote:
        article_vote_entity = ArticleVoteEntity.from_domain_model(article_vote)
        article_vote_entity.save()
        return article_vote_entity.to_domain_model()
```

Вспомним, что паттерн "Репозиторий" подразумевает скрытие деталей и тонкостей
работы с источником данных. "Но позвольте! - скажете Вы, - a где здесь Django?".
Чтобы избежать путаницы со словом "Model", модель данных носит гордое название
`ArticleVoteEntity`. `Entity` также подразумевает, что у неё
имеется уникальный идентификатор ([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/adapter/spi/persistence/entity/article_vote_entity.py)):

```python
# src/myapp/application/adapter/spi/persistence/entity/article_vote_entity.py

class ArticleVoteEntity(models.Model):
    ... # здесь объявлены константы VOTE_UP, VOTE_DOWN и VOTE_CHOICES

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.UUIDField()
    article_id = models.UUIDField()
    vote = models.IntegerField(choices=VOTES_CHOICES)

    ...

    def from_domain_model(cls, article_vote: ArticleVote) -> ArticleVoteEntity:
        ...

    def to_domain_model(self) -> ArticleVote:
        ...
```

Таким образом, всё что происходит в `save_article_vote()` - это
создание Django-модели из доменной модели, сохранение её в БД,
обратная конвертация и возврат доменной модели.
Это поведение легко протестировать.
Например юнит тест удачного исхода выглядит так
[source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/tests/test_myapp/application/adapter/spi/persistence/repository/test_article_vote_repository.py):

```python
# tests/test_myapp/application/adapter/spi/persistence/repository/test_article_vote_repository.py

@pytest.mark.django_db
def test_save_article_vote_persists_to_database(
    article_vote_id: UUID,
    user_id: UUID,
    article_id: UUID
):
    article_vote_repository = ArticleVoteRepository()

    article_vote_repository.save_article_vote(
        ArticleVote(
            id=article_vote_id,
            user_id=user_id,
            article_id=article_id,
            vote=Vote.UP
        )
    )

    assert ArticleVoteEntity.objects.filter(
        id=article_vote_id,
        user_id=user_id,
        article_id=article_id,
        vote=ArticleVoteEntity.VOTE_UP
    ).exists()
```

Одним из требований Django является декларация моделей в `models.py`.
Это решается простым импортированием:

```python
# src/myapp/models.py

from myapp.application.adapter.spi.persistence.entity.article_vote_entity import ArticleVoteEntity
from myapp.application.adapter.spi.persistence.entity.voting_user_entity import VotingUserEntity
```

## Exceptions

Приложение почти готово!. Но вам не кажется, что мы кое-что упустили?
Подсказка: Что произойдёт при голосовании, если ID пользователя или публикации
будет указан неверно? Где-то в недрах Django вылетит исключение `VotingUserEntity.DoesNotExist`,
что на поверхности выльется в неприятный `HTTP 500 - Internal Server Error`,
хотя правильнее было бы вернуть `HTTP 400 - Bad Request` с телом, содержащим
причину ошибки.

Ответ на вопрос, "В какой момент должно быть обработано это исключение?",
вовсе не очевиден. С архитектурной точки зрения, ни API, ни домен не волнуют
проблемы SPI-адаптеров. Максимум что может сделать API с таким исключением -
обработать его в общем порядке, а-ля `except Exception:`.
С другой стороны SPI-порт может предоставить исключение-обётку,
в которую SPI-адаптер завернёт внутреннюю ошибку.
А API может её поймать.

О, я слышу вас, дорогие адепты функционального программирования!
"Какие исключения? В топку! Даёшь `Either`!". В ваших словах
много правды и эта тема заслуживает отдельной статьи.
В одном же, я полностью соглашусь с вами - **в домене не должно быть исключений!**.

Например, в данной ситуации уместным будет исключение `VotingUserNotFound`
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/adapter/spi/persistence/exceptions/voting_user_not_found.py))
в которое оборачивается `VotingUserEntity.DoesNotExist`
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py#L26)):

```python
# src/myapp/application/adapter/spi/persistence/exceptions/voting_user_not_found.py
class VotingUserNotFound(Exception):
    def __init__(self, user_id: UUID):
        super().__init__(user_id, f"User '{user_id}' not found")

# ---

# myapp/application/adapter/spi/persistence/repository/voting_user_repository.py
class VotingUserRepository(GetVotingUserPort):
    ...
    def get_voting_user(self, user_id: UUID, article_id: UUID) -> VotingUser:
        try:
            # Код немного упрощён, в оригинале здесь происходит
            # аннотация флагом "голосовал ли пользователь за статью".
            # см. исходник
            entity = VotingUserEntity.objects.get(id=user_id)
        except VotingUserEntity.DoesNotExist as e:
            raise VotingUserNotFound(user_id) from e

        return self._to_domain_model(entity)
```


А вот теперь действительно, приложение почти готово! Осталось соединить все компоненты
и точки входа.

## Dependencies and application entry point

Традиционно точки входа и маршрутизация HTTP-запросов в Django-приложениях
декларируется в `urls.py`. Всё что нам нужно сделать - это добавить запись
в `urlpatterns`
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/urls.py)):

```python
urlpatterns = [
    path('article_vote', ArticleVoteView(...).as_view())
]
```

Но погодите! Ведь `ArticleVoteView` требует
зависимость имплементирующую `CastArticleVoteUseCase`.
Это конечно же `PostRatingService`... которому
в свою очередь требуются `GetVotingUserPort` и `SaveArticleVotePort`.
Всю эту цепочку зависимостей удобно хранить и управлять
из одного места - контейнера зависимостей
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/dependencies_container.py)):

```python
# src/myapp/dependencies_container.py

...

def build_production_dependencies_container() -> Dict[str, Any]:
    save_article_vote_adapter = ArticleVoteRepository()

    get_vote_casting_user_adapter = VotingUserRepository()

    cast_article_vote_use_case = PostRatingService(
        get_vote_casting_user_adapter,
        save_article_vote_adapter
    )
    article_vote_django_view = ArticleVoteView.as_view(
        cast_article_vote_use_case=cast_article_vote_use_case
    )

    return {
        'article_vote_django_view': article_vote_django_view
    }
```

Этот контейнер инициализируется на старте приложения в
`AppConfig.ready()`
([source](https://github.com/BasicWolf/hexagonal-architecture-django/blob/habr/src/myapp/apps.py)):

```python
# myapp/apps.py

class MyAppConfig(AppConfig):
    name = 'myapp'
    container: Dict[str, Any]

    def ready(self) -> None:
        from myapp.dependencies_container import build_production_dependencies_container
        self.container = build_production_dependencies_container()

```

И наконец `urls.py`:

```python

app_config = django_apps.get_containing_app_config('myapp')
article_vote_django_view = app_config.container['article_vote_django_view']

urlpatterns = [
    path('article_vote', article_vote_django_view)
]
```

## Inversion of Control Containers

Для реализации одного небольшого сценария нам понадобилось создать и связать четыре компонента.
С каждым новым сценарием, число компонентов будет расти и количество связей
будет увеличиваться в арифметической прогрессии.
Как управлять этим зоопарком, когда
приложение начнёт разрастаться до неприличных размеров?
Тут на помощь приходят Kонтейнеры Инверсии Управления.

IoC-container - это фреймворк управляющий объектами и их
зависимостями во время исполнения программы.

Spring был первым _универсальным_ IoC-контейнером / фреймворком
с которым я столкнулся на практике (для зануд: Micronaut - да!).
Чего уж таить, я не сразу проникся заложенными в него идеями.
По-настоящему оценить всю мощь автоматического связывания
(autowiring) и сопутствующего функционала я смог лишь
выстраивая приложение следуя практикам гексагональной архитектуры.

Представьте, насколько удобнее будет использование условного декоратора
`@Component`, который при загрузке программы внесёт класс в реестр
зависимостей и выстроит дерево зависимостей автоматически?

T.e. если зарегестрировать компоненты:

```python
@Component
class ArticleVoteRepository(
    SaveArticleVotePort,
):
    ...

@Component
class VotingUserRepository(GetVotingUserPort):
    ...
```

То IoC-container сможет инициализировать и внедрить их
через консктруктор в другой компонент:

```
@Component
class PostRatingService(
    CastArticleVoteUseCase
):
    def __init__(
        self,
        get_voting_user_port: GetVotingUserPort,
        save_article_vote_port: SaveArticleVotePort
    ):
        ...
```

К сожалению мне не приходилось иметь дела с подобным
инструментарием в экосистеме Питона. Буду благодарен,
если вы поделитесь опытом в комментариях!

## Directory structure

Помните скриншот "типичного Django-приложения"? (#Architecture-is-about-intent)
Сравните его с тем что получилось у нас: TODO: скриншот.
Чувствуете разницу? Нам больше не нужно лезть в файлы в надежде разобраться,
что же там лежит и для чего они предназначены. Более того, теперь даже структура тестов
и кода приложения идентичны! Архитектура приложения видна невооружённым
глазом и существует "на бумаге", а не только в голове у разработчиков приложения.


## Interlude

Давайте дружно выдохнем! Даю честное слово, больше ни одной строчки кода!
Новый сценарий пользования готов к испытаниям.
И пока коллеги вносят последние штрихи (миграция БД, отписки
в трекере задач и т.п.) предлагаю поразмышлять вслух
о том, почему гексагональная архитектура
и предметно-ориентированное проектирование
отлично подходят друг-другу.


## Domain-Driven Design

Эрик Эванс (Eric Evans) популяризировал термин "Domain-Driven Design" в
"большой синей книге" написанной в 2003м году.
[TODO Evans DDD]
И всё заверте... Предметно-ориентированное проектирование - это
методология разработки сложных систем, в которой во главу угла ставится
понимание разработчиками предметной области путем общение с представителями
(экспертами) предметной области и её моделирование в коде.

Мартин Фаулер (Martin Folwer) в своей [статье](https://martinfowler.com/bliki/DomainDrivenDesign.html)
рассуждая о заслугах Эванса подчёркивает, что в этой книге Эванс закрепил терминологию DDD,
которой мы пользуемся и по сей день.

В частности, Эванс ввёл понятие об **Универсальном Языке** (Ubiquitous Language) - языке
который разработчики с одной стороны и эксперты предметной области с другой,
вырабатывают в процессе общения **в течении всей жизни продукта**.
Невероятно сложно создать систему
(а ведь смысл DDD - помочь нам проектировать именно сложные системы!)
не понимая, для чего она предназначена и как ею пользуются.

> У него и команды программистов, которой он руководил, на это ушло более года. Работать было особенно тяжело, потому что заказчик ни за что не хотел сообщить, для каких целей создаются подсистемы. В техническом задании он находил только параметры требуемой системы, но никаких сведений о ее использовании. Недри работал чуть ли не вслепую. И вот теперь, когда система пришла в действие, он не удивился, что в ней оказались скрытые дефекты.
> --- Майкл Карйтон, "Парк юрского периода"

Более того, универсальный язык, со всеми оговорёнными терминами, сущностями,
действиями, связями и т.д. используется при написании программы - в
названиях модулей, функций, методов, классов, констант и даже переменных!


TODO (cut out for russian text): A Bounded Context is a defined part of software where particular terms
definitions and rules apply in a consistent way.

Другой важный термин - **Ограниченный Контекст** (Bounded Context) -
автономные части предметной области с устоявшимися правилами, терминами и определениями.
Простой пример: в онлайн магазине,
модель "товар" несёт в себе совершенно разный смысл для отделов маркетинга,
бухгалтерии, склада и логистики. Для связи моделей товара в этих
контекстах достаточно наличие одинакового идентификатора (например UUID).

Понятие об **Агрегатах** (Aggregate) - наборе объектов
предметной области, с которыми можно обращаться как единым целым,
классификации **объектов-значений** и **объектов-сущностей**.

О DDD можно рассуждать и рассуждать. Эту тему не то что в одну
статью, её и в толстенную книгу-то нелегко уместить.
Приведу лишь несколько цитат, которые помогут
перекинуть мостик между DDD и гексагональной архитектурой:

> Domain is a sphere of knowledge or activity. (Evans, 11)
> Предметная область - это сфера знаний или деятельности.

> Model is a system of abstractions representing selected aspects of a domain. (Evans, 11)
> Модель - это система абстракций, представляющих определённый аспект предметной области.

> Model distills knowledge and assumptions about a domain and is not a way of displaying a reality. (Evans, 11)
> Модель извлекает знания и предположения о предметной области и не является способом отобразить реальность.

> The advantage comes from having a model which fits the specific problem you are trying to solve.
> Преимущество есть лишь у той модели, которая подходит для решения данной проблемы.

Эти цитаты взяты из [выступления Эрика Эванса на конференции DDD Europe 2019го года](https://www.youtube.com/watch?v=pMuiVlnGqjk).
Если вы не знакомы с темой, приглашаю вас насладиться этим выступлением,
прежде чем вы введёте "DDD" в поиск Хабра
и начнёте увлекательное падение в бездонную кроличью нору.
По пути вас ждёт много открытий и куча набитых шишек.
Помню один восхитительный момент:
внезапно в голове сложилась мозаика и пришло озарение,
что фундаментальные идеи DDD и Agile Manifesto имеют общие корни.

## Hexagonal Architecture

Так причём же здесь Гексагональная архитектура?
Я очень надеюсь, что внимательный читатель уже ответил на этот вопрос.

На заре Гексагональной архитектуры в 2005м году, Алистар Кокбёрн [писал](https://alistair.cockburn.us/hexagonal-architecture/):

> Создавайте приложения таким образом, чтобы они могли работать без графического интерфейса или базы данных.
> Тогда вы сможете запускать автоматические регрессионные тесты, работать даже если база данных не доступна
> и связывать приложения между собой без какого-либо стороннеого участия пользователя.

Гексагональная архитектура позволяет элегантно изолировать
части приложения и связять их посредством абстракций.

Становится просто связять  модель предметной
области в коде и "на бумаге" используя универсальный язык
общения с экпертами.
Универсальный язык обогощается с обеих сторон.
При написании кода находятся и изменяются объекты, связи между ними
и всё это перетекает обратно в модель предметной области.

Взаимодействие с внешним миром также упрощается,
ведь оно происходит в рамках изолированых и взаимозаменяемых
компонентов.

Тесты. Тэст-Дривэн Дэвэлопмэнт. В самом соке, когда тест
пишется к пока не существующему функционалу и мы даём возможность
нашей IDE (или по-старинке) создать класс/метод/функцию/концепцию
которая пока существует лишь в тесте.
Интеграционные тесты, для которых не обязательно загружать
всю программу и инфраструктуру, а лишь адаптеры и необходимые
для теста сервисы.

В итоге - приложение, код которого построен на языке бизнеса
и предметной области. Приложение, архитектура которого позволяет
сократить время обратной связи с разработчиками,
экспертами предметной области и  заказчиками.

## Microservices

Подумайте, каким образом в наши дни разбивают приложение
на части, работа которых происходит в ограниченных контекстах?
Ответ очевиден - Микросервисы! Все вышеописанные плюсы
гексагональной архитектуры применимы и в этом случае.
Но помимо вышеописанных плюсов, появляется возможность
модифицировать микросервисы буквально методом "вырезать-вставить".
Можно откреплять целые куски логики и кода из одних
и встявлять в другие, отпочковывать микросервисы из монолита,
или собирать всё обратно в монолит.
И даже не важно, на каких языках написаны эти микросервисы.
Ведь домен изолирован от технической составляющей!
Поэтому переписывание на другой язык программирования
становится куда более тривиальной задачей.
На десерт - короткое видео на тему от Дейва Фарли:
[The problem with microservices](https://www.youtube.com/watch?v=zzMLg3Ys5vI).

## Outro

Спасибо вам уважемый читатель. Спасибо, что не бросили меня в середине статьи
и прошли со мной до конца. Надеюсь тема беседы вас заинтриговала
и вы дерзнёте внедрить принципы гексагональную архитекры и DDD
в ваши проекты. Успехов и до новых встреч!

## P.S.

Хотите проверить, насколько вы прониклись вышеизложенным?
Тогда подумайте и ответьте, является ли поле `VotingUser.voted`
оптимальным решением с точки зрения моделирования предметной
области? А если нет, что бы вы предложили взамен?

## Ссылки

1 - [What is DDD - Eric Evans - DDD Europe 2019](https://www.youtube.com/watch?v=pMuiVlnGqjk)
2 - [Hexagonal architecture, Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
