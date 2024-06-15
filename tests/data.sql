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


INSERT INTO ITEM (USER_ID, FOLDER_ID, NAME, USERNAME, PASSWORD, URI, NOTES)
VALUES 
    (
        '1',-- user 1
        '2', -- folder 2
        'Fake Name', 
        'gAAAAABmWxC258GXTjpFXPauNJD8Bx7QoC3ErN_-esqi7wg4F46sjOQTLpumMOeWGw3eckns5A8Vvml6T3L_DBhFGAj8Bouq-Q==',--'Fake Username',
        'gAAAAABmWxDqNfCLv1twNzBsOW4A3pR-xRkR9rDFkhZFUeDeXAK_A9wOWkXzpubK5Q80hBHiIFcAyciZIivdXGRlOQkizZ6JHA==',--'asdf1234',
        'gAAAAABmWxEmuGdhPyUIBboX1JBviHPrFqHhF84qqhAcEKKS6UbQ0qJUgF5hYgK-t42C4XGRRmSqOh8w6478NHAokSrAClfS8A==',--'www.google.com',
        'gAAAAABmWxFRYsLdWk1MRpIKOtatEeueSJ5THi2xLHvzea6ZLcZk8ii7Br96nEy84vpbhXSy5Uq4ka13R2KLmb3ZnoSxujqCwg=='--'note'    
    ),
    (
        '2', -- user 2
        '3', -- folder 3
        'other user',
        'gAAAAABmX1ETqp-DM_aRaREkjivpP4uOpcCsn4CN27AB0tT9UR1t3bApgEEYUyNeEud4Np4t0nl5rBO6Nahmc1qWBlmmHzJJq9cqtPzgj1dO6vHN9GMkDjo=', --otheruser username
        'gAAAAABmX1E5IkTiOOi6CSBHqSAFcYQ61pFvoEo3z-kMlN2VFV_TeArjat2wsS_1kvwYM0WV7o6IRICAO82jRJcHfvp8r9W4pkiSe1E3INkaFpquwumMUac=', --otheruser password
        'gAAAAABmX1FTrrviVO7X-9oZHufGGmBeNijnX-k98aOOUff8VuASIocfkOcYYPeb6mSKuOTxbJ0qWCtgodiw1ih7U8pWQneOcXxm01tRKaSgAroTubXuVR4=', --www.otherusersite.com
        'gAAAAABmX1FzkDPPErYQlmIzPp9bW-PDZU0yqfyUOHr5b2l2eoTGJtaD5A81YQ70Mz8NUGuMYFLy1-Jdj0ZJRawz7WkAhcOEGw==' -- otherusers note

    ),
    (
        '1', -- user 2
        '2', -- folder 3
        'Delete item',
        'gAAAAABmX1ETqp-DM_aRaREkjivpP4uOpcCsn4CN27AB0tT9UR1t3bApgEEYUyNeEud4Np4t0nl5rBO6Nahmc1qWBlmmHzJJq9cqtPzgj1dO6vHN9GMkDjo=', --otheruser username
        'gAAAAABmX1E5IkTiOOi6CSBHqSAFcYQ61pFvoEo3z-kMlN2VFV_TeArjat2wsS_1kvwYM0WV7o6IRICAO82jRJcHfvp8r9W4pkiSe1E3INkaFpquwumMUac=', --otheruser password
        'gAAAAABmX1FTrrviVO7X-9oZHufGGmBeNijnX-k98aOOUff8VuASIocfkOcYYPeb6mSKuOTxbJ0qWCtgodiw1ih7U8pWQneOcXxm01tRKaSgAroTubXuVR4=', --www.otherusersite.com
        'gAAAAABmX1FzkDPPErYQlmIzPp9bW-PDZU0yqfyUOHr5b2l2eoTGJtaD5A81YQ70Mz8NUGuMYFLy1-Jdj0ZJRawz7WkAhcOEGw==' -- otherusers note

    );


INSERT INTO FOLDER (USER_ID, FOLDER_NAME)
VALUES 
    (
        '1',
        'Example Folder'
    ),
    (
        '1',
        'Passing Folder'
    ),
    (
        '2',
        'Other users Folder'
    );