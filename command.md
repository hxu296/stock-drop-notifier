# Telegram command manual

Below is a list of Telegram commands that can be used to customize search filter as well as list, add, and remove notifiers. The exact instruction can also be accessed by sending /help command to the Telegram bot.

#### /help ####
Show the command help page.

#### /example ####
Show how a series of commands work in application.

#### /list ####
List filter or notifier information. Upon sending /list, a keyboard menu will show up for more options. This command does not require any parameter. 

#### /add ####
Add a notifier using the current filter. This command does not require any parameter, but it can only be used after all required fields of filter are specified.

#### /rm ####
Remove one or more notifiers by id, which can be found using /list. Examples of this command are as follows:
- /rm 12391
- /rm 31259 50028

#### !search ####
This command is used to customize the search_words parameter of a filter, which is a ***required*** parameter filed. To use this command, follow !search with a list of space-separated words for whom a newly added notifier will search. Examples of this command are as follows:
- !search "Play Station 5", PS5
- !search 3080 3060ti

#### !forbid ####
This command is used to customize the forbidden_words parameter of a filter, which is an ***optional*** parameter filed, but we highly recommend using it. The format of this command is similar to that of !search. This command helps to exclude pages that have forbidden_words in product titiles. Examples of this commands are as follows:
- !forbid "Play Station 4" PS4
- !forbid 2080 2070 2060

#### !price #### 
This command is used to customize the price_ceiling parameter of a filter, which is a ***required*** parameter filed. To use this command, follow !price with a non-negative integer. A newly added notifier will stop listening to products that are above this price line. Examples are as follows:
- !price 1000 

#### !freq ####
This command is used to customize the request_frequency parameter of a filter, which is an ***optional*** parameter field. request_frequency is a non-negative floating-point number where, for example, 0.2 means sending 0.2 query per second to newegg, effectively equivalent to waiting 5 seconds before next refresh. As websites also use request frequency for scalper detection, there is a trade off between notifier efficiency and stability. If unspecified, request_frequency will default to 0.3, which is found to be the sweet point of this trade off. Examples of this commands are as follows:
- !freq 0.2
- !freq 0.5

#### !rest ####
This command is used to customize the rest_time parameter of a filter, which is an ***optional*** parameter filed. rest_time are two integers in range [0, 23] between which the notifier will stop working. As most websites use request times for scalper detection, this feature is added to improve the stability of notifier. If unspecified, rest_time parameter will default to 23, 8, meaning the notifier will stop working from 23:00 to 8:00. Examples of this commands are as follows:
- !rest 1 9
- !rest 23 8





