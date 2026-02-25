# Звіт: Лабораторна робота 1

[Репозиторій проєкту](https://data.gov.ua/dataset/ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb)

# Що було практично засвоєно

 - Основи github: Я навчився ініціалізувати git-репозиторій, додавати зміни в процеси комітів і виконувати push команди в особистий репозиторій в GitHub.
 - Процес створення гілок: Практикувався створювати та змінювати гілки. Основною їхньою метою є зміни і експерименти всередині них, які не зачіпають головну гілку (main)
 - Злиття: Освоїв процес злиття (merging) гілок в головну гілку main, вирішував сценарій з merge конфліктами.

# Що було зроблено

- Створив git-репозиторій для мого проекту
- Створив головну гілку main і feature гілки для додавання змін та нових функцій.
- Ініціалізував коміти з короткими описом змін, які я створював.
- Завантажив мої зміни в GitHub і створював пул реквести, щоби злити зміни моїх feature гілок на головну гілку main.
- Створив файл CHANGELOG.md для відслідковування змін проекту.

# Вивід команди ```git log --oneline --graph --all```

```
* 667e46f Update title in README.md
* f96800f feat: add data visualization
| * dda103f feat: add data visualization
|/  
* 10f5637 docs: change readme file
| * a319005 docs: change readme file
|/  
* d9de624 docs: change readme (#4)
| * 64c592c docs: change readme
|/  
* 4dcfeff feat: add data and model analysis (#3)
* 98bb0c9 feat: add exploratory data analysis (#2)
| * 4457602 feat: add data and model analysis
|/  
| * e1608fe feat: add exploratory data analysis
|/  
*   c0d6b46 Merge pull request #1 from Roman-BodnarSHI11/feature/data_load
|\  
| * a588cbc add script to load data
|/  
* 038e599 initial commit
```