-- Таблица арендатора (customer)
CREATE TABLE IF NOT EXISTS public.customer
(
    "IDCustomer" serial NOT NULL,
    "INN" BIGINT NOT NULL,
    "Status" VARCHAR(20) NOT NULL,
    "Customer" VARCHAR(60) NOT NULL,
    "AddressCust" VARCHAR(250) NOT NULL,
    "Bank" VARCHAR(60) NOT NULL,
    "Account" VARCHAR(20) NOT NULL,
    "Tax" VARCHAR(60) NOT NULL,
    "Chief" VARCHAR(40) NOT NULL,
    "Phone" VARCHAR(20) NOT NULL,
    CONSTRAINT customer_pkey PRIMARY KEY ("IDCustomer"),
    CONSTRAINT inn_unique UNIQUE ("INN")
);

ALTER TABLE public.customer
    OWNER to postgres;

-- Таблица ответственных от агенства (employees)
CREATE TABLE IF NOT EXISTS public.employees
(
    "IDEmployee" serial NOT NULL,
    "Employee" VARCHAR(60) NOT NULL,
    CONSTRAINT employee_pkey PRIMARY KEY ("IDEmployee")
);

ALTER TABLE public.employees
    OWNER to postgres;

-- Таблица периодов оплаты
CREATE TABLE IF NOT EXISTS public.periods
(
    "IDPeriod" serial NOT NULL,
    "Period" VARCHAR(60) NOT NULL,
    CONSTRAINT period_pkey PRIMARY KEY ("IDPeriod")
);

ALTER TABLE public.periods
    OWNER to postgres;

-- Таблица рекламных щитов (billboard)
CREATE TABLE IF NOT EXISTS public.billboard
(
    "IDBillboard" serial NOT NULL,
    "Address" VARCHAR(60) NOT NULL,
    "Orientation" VARCHAR(60) NOT NULL,
    "Square" NUMERIC(10, 2) NOT NULL,
    "District" VARCHAR(20) NOT NULL,
    "Size" VARCHAR(20) NOT NULL,
    "Picture" VARCHAR(250),
    CONSTRAINT regnumber_pkey PRIMARY KEY ("IDBillboard")
);

ALTER TABLE public.billboard
    OWNER to postgres;

-- Таблица договоров (treaty)
CREATE TABLE IF NOT EXISTS public.treaty
(
    "IDTreaty" serial NOT NULL,
    "DateStart" date NOT NULL,
    "StopDate" date NOT NULL,
    "SignDate" date NOT NULL,
    "Advertisement" boolean NOT NULL,
    "Cost" NUMERIC(10, 2) NOT NULL,
    "Leasing" NUMERIC(10, 2) NOT NULL,
    "PeriodID" INTEGER NOT NULL,
    "EmployeeID" INTEGER NOT NULL,
    "BillboardID" INTEGER NOT NULL,
    "CustomerID" INTEGER NOT NULL,
    CONSTRAINT treaty_pkey PRIMARY KEY ("IDTreaty"),
    CONSTRAINT employee_fkey FOREIGN KEY ("EmployeeID")
        REFERENCES public.employees ("IDEmployee") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT period_fkey FOREIGN KEY ("PeriodID")
        REFERENCES public.periods ("IDPeriod") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT billboard_fkey FOREIGN KEY ("BillboardID")
        REFERENCES public.billboard ("IDBillboard") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT customer_fkey FOREIGN KEY ("CustomerID")
        REFERENCES public.customer ("IDCustomer") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE public.treaty
    OWNER to postgres;

-- Таблица пользователей (пароль - sha1)
CREATE TABLE public.users(
    "IDUser" serial PRIMARY KEY NOT NULL,
    "Login" VARCHAR(32) UNIQUE NOT NULL,
    "Password" VARCHAR(40) NOT NULL,
    "is_admin" boolean NOT NULL
);

ALTER TABLE public.users
    OWNER to postgres;

-- Арендаторы
INSERT INTO public.customer
("INN", "Status", "Customer", "AddressCust", "Bank", "Account", "Tax", "Chief", "Phone")
VALUES
(1242005939, 'ООО', 'Дельта-Тест', 'г.Владивосток, ул.Никифорова, 2А', 'Примтеркомбанк', '40817810099910004312', 'МИФНС России №9 по Приморскому краю', 'Нигматуллин Руслан Насимович', '89141524687'),
(1276069176, 'ООО', 'Транстехсервис', 'г.Владивосток, ул.Луговая, 59', 'Морской банк', '40817810099910004588', 'МИФНС России №12 по Приморскому краю', 'Романов Роман Анатольевич', '89241545223'),
(1012002692, 'ОАО', 'Защита-Лес', 'г.Находка, ул.Пограничная, 6, 219', 'Банк Синара', '40817810099910008946', 'МИФНС России №15 по Приморскому краю', 'Гринберг Самоил Израилович', '89043874930');

-- Отвественные от агенства
INSERT INTO public.employees ("Employee")
VALUES
('Иванов'),
('Петров'),
('Сидоров'),
('Рогов');

-- Периоды оплаты
INSERT INTO public.periods ("Period")
VALUES
('ежемесячная'),
('квартальная'),
('годовая');

-- Рекламный щит
INSERT INTO public.billboard
("Address", "Orientation", "Square", "District", "Size", "Picture")
VALUES
('г.Владивосток, ул.Стрелковая, 46', 'ОДОРА', 18, 'Ленинский', '3x6', null),
('г.Владивосток, ул.Снеговая, 32', 'ОДОРА', 18, 'Первореченский', '3x6', null),
('г.Владивосток, ул.Героев-тихоокеанцев, 23А', 'Депо-2', 36, 'Первомайский', '3x12', null),
('г.Владивосток, ул.Алеутская, 14', 'ОДОРА', 18, 'Фрунзенский', '3x6', null);

-- Договоры
INSERT INTO public.treaty ("DateStart", "StopDate", "SignDate", "Advertisement", "Cost", "Leasing", "PeriodID", "EmployeeID", "BillboardID", "CustomerID")
VALUES
('2021-03-02', '2021-04-27', '2021-03-01', true, 15000, 28000, 1, 1, 1, 1),
('2021-05-19', '2021-06-19', '2021-05-02', true, 20000, 34000, 1, 2, 3, 2),
('2021-06-20', '2021-12-31', '2021-06-08', false, 0, 12000, 2, 3, 4, 3);

-- Пользователи
INSERT INTO public.users ("Login", "Password", "is_admin")
VALUES
('admin1', '9d516530dba7ae296eac0599b016c6038f230397', true),
('user1', '9d516530dba7ae296eac0599b016c6038f230397', false);
