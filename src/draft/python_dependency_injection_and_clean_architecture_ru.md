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


## Пролог


Полтора года назад я сменил место работы и расставшись с миром Python/Django,
окунулся в мир Kotlin/Spring Boot.
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
Несмотря на это, его легко поддерживать, тестировать, развивать -
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
Оглядываясь назад понимаю, что не смог бы написать *так* хорошо
опираясь лишь на старый опыт. И даже небольшие крупицы
знаний помогают программировать и решать проблемы бизнеса эффективнее.


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
чтобы это протестировать. Что, что? `mock.patch(...)` говорите?
Коллеги, давайте попробуем зайти с другой стороны.

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
#
def test_send_alert_sends_message_to_alert_topic()
    message_bus_mock = MessageBusMock()
    send_alert(message_bus_mock, "A week of astrology at Habrahabr!")

    assert message_bus_mock.sent_to_topic == 'alert'
    assert message_bus_mock.sent_message = message

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

Давайте попытаемся решить эту проблему посредством ООП:

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
Мы **внедряем** эту зависимость в момент создания объекта `AlertDispatcher`,
посредством передачи зависимости в метод `__init__()`. Мы **связали**
(we have **wired**, не путать с **coupling**!) объект и его зависимость.

Но теперь акцент смещается с `message_bus` на `alert_dispatcher`!
Этот **компонент** может понадобиться в различных местах приложения.
Мало ли откуда нужно оправить сигнал тревоги!
Необходим некий глобальный **контекст** который будет управлять
инициализацией и связыванием компонентов. И в небольшом
приложении эту задачу можно вполне решить своими силами.

## Componential architecture

Говоря о внедрении зависимостей мы не сильно заостряли внимание
на типах. Но вы надерное догадались, что `MessageBus` - это всего
лишь абстракция, интерфейс, или как бы
сказал PEP-544 - протокол. Т.е. где-то в нашем приложении объявленo:

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
Действительно, давайте запихнём это приложение в одну функцию:

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
жизнь. Но простит ли растущее приложение такой сжатый подход?

Давайте же вернёмся к нашей компонентной архитекруте. В чём её
преимущества?

* Компоненты **изолированы** и не зависимы друг от друга напрямую.
  Вместо этого они **связаны посредством абстракций**.
* Каждый компонент работает в чётких рамках и **решает лишь одну задачу**.
* Это значит, что компоненты могут быть протестированы как в полной изоляции так и в
  любой произвольной комбинации, включающей тестовых двойников (test double).
  Думаю не стоит объяснять, насколько проще тестировать изолированные
  части программы. Подход к TDD меняется с "мы пишем тесты" на
  ~~"тесты утром, вечером код"~~ "сначала пишем тест, потом пишем код".
* С учётом того, что зависимости описываются абстракциями, можно
  безболезненно заменить один компонент другим. В нашем примере -
  вместо `MemoryMessageBus` можно бухнуть `DbMessageBus` да хоть
  в файл на диске писать - тому, кто вызывает `message_bus.send(...)`
  нет до этого никакого дела.

"Да это же SOLID!" - скажите вы. И будете абсолютно правы.
Не удивлюсь, если у вас возникло чувство дежа-вю, ведь
уважаемый @zueve совсем недавно
детально описал связь SOLID и Чистой архитекруты
в статье "Clean Architecture глазами Python-разработчика".
И наша компонентная архитектура находится лишь в шаге от
гексагональной архитекруты.
Кстати, причём тут гексагон?


## Hexagonal architecture of Ports and Adapters

"У нас Гексагональная архитектура портов и адаптеров" -
эта фраза открывает рассказ об архитектуре приложения
новым членам команды.
На картинке это выглядит так:

[КАРТИНКА]

Домен (предметная область) - это сердце приложения.
Именно здесь лежит код отвечающий за выполнение бизнес-логики.
Именно здесь названия функций, классов, констант и других объектов
повторяют язык экспертов предметной области.
Здесь выполняются правила из разряда "Если в корзине
товара на 1000 рублей, предложите бесплатную доставку".
Здесь нет места HTTP, SQL, RabbitMQ, AWS и т.д. и т.п.

Зато всему этому празднику технологий есть место в **адаптерах**
подсоединяемых к **портам**. Команды в приложение поступают
через **ведущие** (driven) или **API** порты.
Команды которые отдаёт приложение поступают в **ведомые** порты (driven port).
Их также называют портами интерфейса поставщика услуг (Service Provider Interface, SPI).

Mежду портами и доменом сидят дирижёры - **серсивы приложения** (Application services).
Они являются *связующим звеном* между доменом и различными сценариями использования
с одной стороны и ведущими и ведомыми портами с другой.

Всё это - и порты, и адаптеры и сервисы приложения и даже домен - **слои**
архитектуры. И единственной заповедью взаимодействия между слоями является
"Зависимости всегда направлены от внешних слоёв к центру приложения".
Например, адаптер может ссылаться на домен, но не наоборот.

И... ВСЁ. Это - вся суть архитектуры нашего приложения. А точнее -
архитектура *некоторых* микросервисов. Она замечательно подходит
для задач с богатой и обширной предметной областью.
Для голого CRUDа такая архитектура избыточна - Active record вам в руки.
Давайте же немного углубимся в детали и рассмотрим как связана
эта и "компонентная" архитектура описанная выше.


## Driver and driven ports

Представьте, что мы разрабатываем интернет-магазин
и нам нужно реализовать обычный для таких
приложений сценарий пользования: "Добавить товар в корзину".
Переводя это на язык архитекруты - в наше приложение
нужно добавить ведущий порт `AddProductToBasketUseCase`:


```python
# application/ports/api/add_item_to_basket_use_case.py

class AddItemToBasketUseCase(typing.Protocol):
    def add_item_to_basket(self, basket_id: UUID, product_id: UUID, count: int)
        pass
```

Заметьте, что `AddItemToBasketUseCase`, как и все порты в нашей архитектуре
- это голая абстракция aka интерфейс.

Чуть позже мы поговорим о компоненте, который имплементирует этот порт.
Пока же подумаем, как будет вызываться этот сценарий? Ведь он, например, может
вызываться по какому-то сообщению из шины RabbitMQ.
Но скорее всего это будет REST-адаптер:

```python
# adapter/rest/basket_item_controller.py

from some_http_framework import post

from myshop.application.ports.api import AddItemToBasketUseCase

class BasketItemController:
    def __init__(self, add_item_to_basket_use_case: AddItemToBasketUseCase)
        self._add_item_to_basket_use_case = add_item_to_basket_use_case

    @post('/basket/{basket_id}/items')
    def add_item(self, basket_id: UUID, item: BasketItemDto):
        basket_item_id = self._add_item_to_basket_use_case
            .add_item_to_basket(basket_id, item.product_id, item.count)

        return basket_item_id
```

Заметьте, что уже на этом этапе мы можем применить практики TDD, и
начать с юнит-теста. "Позвольте, а как же `AddItemToBasketUseCase`? -
спросите вы. Очень просто. Это же абстракция! Её конкретной
имплементацией может быть тестовый двойник, например
тот же `unittest.mock.MagicMock`. Давайте так и

```python
# test/adapter/rest/test_basket_item_controller.py


def test_add_item_to_basket(http_client, add_item_to_basket_use_case):

```

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