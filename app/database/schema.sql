
CREATE TABLE USERS{
    login VARCHAR(255) PRIMARY,
    password VARCHAR(255) NOT NULL ,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
};

CREATE TABLE CONTACTS{
    owner VARCHAR(255) PRIMARY
    login VARCHAR(255) NOT NULL
    FOREIGN KEY(login) REFERENCES USERS(login)
};