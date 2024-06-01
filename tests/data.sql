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

/*
Changed to encrypted items.
See below
INSERT INTO ITEM (USER_ID, FOLDER_ID, NAME, USERNAME, PASSWORD, URI, NOTES)
VALUES 
    (
        '1',
        '2',
        'Fake Name', 
        'Fake Username',
        'asdf1234',
        'www.google.com',
        'note'    
    );
*/
INSERT INTO ITEM (USER_ID, FOLDER_ID, NAME, USERNAME, PASSWORD, URI, NOTES)
VALUES 
    (
        '1',
        '2',
        'Fake Name', 
        'gAAAAABmWxC258GXTjpFXPauNJD8Bx7QoC3ErN_-esqi7wg4F46sjOQTLpumMOeWGw3eckns5A8Vvml6T3L_DBhFGAj8Bouq-Q==',--'Fake Username',
        'gAAAAABmWxDqNfCLv1twNzBsOW4A3pR-xRkR9rDFkhZFUeDeXAK_A9wOWkXzpubK5Q80hBHiIFcAyciZIivdXGRlOQkizZ6JHA==',--'asdf1234',
        'gAAAAABmWxEmuGdhPyUIBboX1JBviHPrFqHhF84qqhAcEKKS6UbQ0qJUgF5hYgK-t42C4XGRRmSqOh8w6478NHAokSrAClfS8A==',--'www.google.com',
        'gAAAAABmWxFRYsLdWk1MRpIKOtatEeueSJ5THi2xLHvzea6ZLcZk8ii7Br96nEy84vpbhXSy5Uq4ka13R2KLmb3ZnoSxujqCwg=='--'note'    
    );

