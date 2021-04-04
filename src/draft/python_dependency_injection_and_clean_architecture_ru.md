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
первого попавшегося Django-приложения с Гитхаба.

Роберт Мартин развивает идею [дальше](https://www.youtube.com/watch?v=WpkDN78P884).
Взгляните на архитектурный план этажа и догадайтесь,
для чего предназначено это здание?

TODO

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

С чего же начать работу? Конечно же с построения модели предметной области!

## Domain model

Давайте ещё раз внимательно прочтём требования и подумаем,
как описать "пользователя голосующего за публикацию"?
Проще показать в коде, чем описывать словами:

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

Вглядевшись в сие творение я задался вопросом:
а с чего это пользователь описывается именно такими набором данных (полями класса)?
Почему бы не задать его как `voted_for_articles: Set[UUID]`?
Как вы думаете, нужно ли знать голосовал ли пользователь за другие публикации,
чтобы проголосовать за данную публикацию? Наверняка нет!
Хорошо, а что такое `Vote` и `CastArticleVoteResult`?

```python
# src/myapp/application/domain/model/vote.py

# Обозначает голос "За" или "Против"
class Vote(Enum):
    UP = 'up'
    DOWN = 'down'
```

В свою очередь `CastArticleVoteResult` - это тип объединяющий оговорённые исходы
сценария:  `ГолосПользователя`, `НедостаточноКармы`, `ПользовательУжеГолосовалЗаПубликацию`:
[TODO: source].
```
# src/myapp/application/domain/model/cast_article_vote_result.py
...
CastArticleVoteResult = Union[ArticleVote, InsufficientKarma, VoteAlreadyCast]
```

Как вы думаете, какие данные должен нести в себе результат
успешного выполнения сценария `ArticleVote`?

<spoiler title="Ответ">
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
И начнём мы конечно же с тестов. [TODO: source]
Первый же тест нацелен на проверку успешного выполнения сценария:

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
и кодом, с каждым тестом дописывая сценарий до полной готовности:

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

На этом мы закончим моделирование предметной области.
Если у вас остались вопросы по реализации остальных моделей,
приглашаю вас взглянуть на исходный код TODO:link.

## Driver port: Cast article vote use case

Как было сказано ранее, в гексагональной архитектуре,
приложение управляется через API-порты.

Чтобы как-то дотянуться до доменной модели, в наше приложение
нужно добавить ведущий порт `CastArticleVotingtUseCase`, который
принимает ID пользователя, ID публикации, значение голоса: за или против
и возвращает результат выполненного сценария.

TODO: КАРТИНКА

```python
# src/myapp/application/ports/api/cast_article_vote/cast_aticle_vote_use_case.py

class CastArticleVoteUseCase(Protocol):
    def cast_article_vote(self, command: CastArticleVoteCommand) -> CastArticleVoteResult:
        raise NotImplementedError()
```

Все входные параметры сценария обёрнуты в единую структуру-команду
`CastArticleVoteCommand` [source](http://todo),
а все возможные результаты объединены - это уже знакомое объединение типов
`CastArticleVoteResult` [source](http://todo-anchor):

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

TODO: КАРТИНКА

Наш HTTP адаптер, или на языке Django и DRF - `View`, до безобразия
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
    # ему в конструкторе.
    # Ответ на вопрос "Почему не MagicMock?" будет дан в
    # конце статьи TODO.
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
`VoteAlreadyCast`. Адаптеру остаётся правильно обработать этот результат и
сформировать `HTTP Response`. Остаётся протестировать, соответствует ли
сформированный ответ и его статус ожидаемым значениям.

TODO:
Ещё раз попрошу заметить, насколько *облегчённее* становится тестирование, когда
 не нужно загружать всё приложение целиком. Адепты Django
вспомнят о легковесном тестировании вьюшек посредством `RequestFactory`.
Но гексагональная архитектура позволяет шагнуть дальше.
Мы избавились от обезьяних патчей и mock-обёрток конкретных классов.
Мы легко управляем поведением зависимостей нашего `View`,
ведь взаимодействие с ними происходит через абстрактный интерфейс.
И всё это - легко модифицировать и отлаживать.

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
(TODO: [source](http://) ):

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

    def __init__(
        self,
        get_voting_user_port: GetVotingUserPort,
        save_article_vote_port: SaveArticleVotePort
    ):
        self._get_voting_user_port = get_voting_user_port
        self._save_article_vote_port = save_article_vote_port

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
(TODO: [source](http://) ): (TODO: [source](http://) ).
Давайте приведём один из интерфейсов здесь:

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
в виде ссылки на исходник (TODO: [source](http://) ) [TODO] и двинуться
дальше.

## SPI Ports and Adapters

Продолжим рассматривать SPI-порты и адаптеры на примере
``SaveArticleVotePort``. К этому моменту можно было и забыть,
что мы всё ещё надохимдя в рамках Django. Ведь до сих
пор не было написано того, с чего обычно начинается
любое Django-приложение - модели данных!
Тем не менее, не стоит торопиться. Начнём с адаптера,
имплементирующего вышеуказанный порт:

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
работы с источником данных. И как видно из кода, наш репозиторий справляется с этой
задачей на ура. "Но позвольте! - скажете Вы, - a где здесь Django?".
Чтобы избежать путаницы со словом "Model", модель данных носит гордое название
`ArticleVoteEntity`. `Entity` в данном случае также подразумевает, что у неё
имеется уникальный идентификатор:
(TODO: [source](http://) )

```python
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
Это поведение легко протестировать. (TODO: [source](http://) )
Например юнит тест удачного исхода выглядит так:

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

```
# src/myapp/models.py

from myapp.application.adapter.spi.persistence.entity.article_vote_entity import ArticleVoteEntity
from myapp.application.adapter.spi.persistence.entity.voting_user_entity import VotingUserEntity
```

Приложение почти готово! Осталось соединить все компоненты
и связать точки входа. 

## Dependencies and application entry point

Традиционно точки входа и маршрутизация HTTP-запросов в Django-приложениях
декларируется в `urls.py`. Всё что нам нужно сделать - это добавить запись
в urlpatterns:

```python
urlpatterns = [
    path('article_vote', ArticleVoteView(...).as_view())
]
```

Погодите рваться в бой! Ведь `ArticleVoteView` требует
зависимость имплементирующую `CastArticleVoteUseCase`.
Это конечно же `PostRatingService`... которому 
в свою очередь требуются `GetVotingUserPort` и `SaveArticleVotePort`.
Всей этой цепочкой зависимостей удобно управлять
из одного места - контейнера зависимостей:

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
`AppConfig.ready()`:

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



* https://github.com/basicWolf/hexagonal-architecture-django

* Transactions
* Mocks
