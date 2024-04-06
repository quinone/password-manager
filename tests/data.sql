INSERT INTO USER (NAME, EMAIL, PASSWORD, PASSWORD_HINT)
VALUES
    (
        'test', 
        'test@test.com', 
        '$argon2id$v=19$m=65536,t=3,p=4$Sj63XHk3zU0yrlrO2OOKlQ$p3utNwpLmt4/BN/lA1kmrTyErP8EMjf6JQYjw/lxcyg',
        'The password is "testpassword"'
    ),
    (
        'other',
        'other@google.com',
        '$argon2id$v=19$m=65536,t=3,p=4$bcra4HaJs0KTWz7VJF+KCg$Misjfg/IRLLKlluRW9WoY4HzoO5z2QsJ5GitIo6wjEs',
        'The password is "other"'
    );