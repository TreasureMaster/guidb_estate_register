-- Таблица материала стен (materials)
CREATE TABLE IF NOT EXISTS public.materials
(
    "IDMaterial" serial NOT NULL,
    "Material" VARCHAR(60) NOT NULL,
    CONSTRAINT material_pkey PRIMARY KEY ("IDMaterial")
);

ALTER TABLE public.materials
    OWNER to postgres;

-- Таблица зданий (buildings)
CREATE TABLE IF NOT EXISTS public.buildings
(
    "IDKadastr" serial NOT NULL,
    "BuildingName" VARCHAR(60) NOT NULL,
    "Land" NUMERIC(10, 2) NOT NULL,
    "Address" VARCHAR(250) NOT NULL,
    "Year" SMALLINT NOT NULL,
    "Wear" SMALLINT NOT NULL,
    "Flow" SMALLINT NOT NULL,
    "Picture" VARCHAR(250),
    "Comment" TEXT,
    "MaterialID" INTEGER NOT NULL,
    CONSTRAINT kadastr_pkey PRIMARY KEY ("IDKadastr"),
    CONSTRAINT material_fkey FOREIGN KEY ("MaterialID")
        REFERENCES public.materials ("IDMaterial") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE public.buildings
    OWNER to postgres;

-- Таблица назначения помещения (targets)
CREATE TABLE IF NOT EXISTS public.targets
(
    "IDTarget" serial NOT NULL,
    "Target" VARCHAR(60) NOT NULL,
    CONSTRAINT target_pkey PRIMARY KEY ("IDTarget")
);

ALTER TABLE public.targets
    OWNER to postgres;

-- Таблица кафедр (departments)
CREATE TABLE IF NOT EXISTS public.departments
(
    "IDDepartment" serial NOT NULL,
    "DepartmentName" VARCHAR(60) NOT NULL,
    "Boss" VARCHAR(60) NOT NULL,
    "Phone" BIGINT NOT NULL,
    "OfficeDean" VARCHAR(60) NOT NULL,
    CONSTRAINT department_pkey PRIMARY KEY ("IDDepartment")
);
-- Зачем Здание и Ответственный ?

ALTER TABLE public.departments
    OWNER to postgres;

-- Таблица помещений (halls)
CREATE TABLE IF NOT EXISTS public.halls
(
    "IDHall" serial NOT NULL,
    "HallNumber" SMALLINT NOT NULL,
    "HallSquare" NUMERIC(10, 2) NOT NULL,
    "Windows" SMALLINT NOT NULL,
    "Heaters" SMALLINT NOT NULL,
    "TargetID" INTEGER NOT NULL,
    "DepartmentID" INTEGER NOT NULL,
    "KadastrID" INTEGER NOT NULL,
    CONSTRAINT halls_pkey PRIMARY KEY ("IDHall"),
    CONSTRAINT target_fkey FOREIGN KEY ("TargetID")
        REFERENCES public.targets ("IDTarget") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT department_fkey FOREIGN KEY ("DepartmentID")
        REFERENCES public.departments ("IDDepartment") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT kadastr_fkey FOREIGN KEY ("KadastrID")
        REFERENCES public.buildings ("IDKadastr") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE public.halls
    OWNER to postgres;

-- Таблица ответственных (chiefs)
CREATE TABLE IF NOT EXISTS public.chiefs
(
    "IDChief" serial NOT NULL,
    "Chief" VARCHAR(60) NOT NULL,
    "AddressChief" VARCHAR(120) NOT NULL,
    "Experience" SMALLINT NOT NULL,
    CONSTRAINT chiefs_pkey PRIMARY KEY ("IDChief")
);

ALTER TABLE public.chiefs
    OWNER to postgres;

-- Таблица имущества (units)
CREATE TABLE IF NOT EXISTS public.units
(
    "IDUnit" serial NOT NULL,
    "UnitName" VARCHAR(60) NOT NULL,
    "DateStart" DATE NOT NULL,
    "Cost" NUMERIC(10, 2) NOT NULL,
    "CostYear" SMALLINT NOT NULL,
    "CostAfter" NUMERIC(10, 2) NOT NULL,
    "Period" VARCHAR(60) NOT NULL,
    "HallID" INTEGER NOT NULL,
    "ChiefID" INTEGER NOT NULL,
    CONSTRAINT units_pkey PRIMARY KEY ("IDUnit"),
    CONSTRAINT hall_fkey FOREIGN KEY ("HallID")
        REFERENCES public.halls ("IDHall") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT chief_fkey FOREIGN KEY ("ChiefID")
        REFERENCES public.chiefs ("IDChief") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE public.units
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

-- Материал здания
INSERT INTO public.materials ("Material")
VALUES
('Кирпич'),
('Дерево'),
('Железобетон'),
('Пеноблок');

-- Здания
INSERT INTO public.buildings
("BuildingName", "Land", "Address", "Year", "Wear", "Flow", "Picture", "Comment", "MaterialID")
VALUES
('Административное', 4000, 'ул.Никифорова, 2А', 1982, 50, 5, null, null, 1),
('Корпус 1', 3000, 'ул.Луговая, 59', 1985, 20, 3, null, null, 3),
('Корпус 2', 3200, 'ул.Пограничная, 6', 1986, 30, 3, null, null, 3);

-- Назначение помещения
INSERT INTO public.targets ("Target")
VALUES
('аудитория'),
('лаборатория'),
('вычислительный центр'),
('деканат');

-- Кафедра
INSERT INTO public.departments
("DepartmentName", "Boss", "Phone", "OfficeDean")
VALUES
('Философия', 'Ячин Сергей Евгеньевич', 842322652424, 'Гуманитарные науки'),
('Социальные науки', 'Кузина Ирина Геннадьевна', 842322652424, 'Гуманитарные науки'),
('Психология', 'Батурина Оксана Сергеевна', 842322652424, 'Гуманитарные науки'),
('История и археология', 'Пахомов Олег Станиславович', 842322652424, 'Гуманитарные науки');

-- Помещения
INSERT INTO public.halls
("HallNumber", "HallSquare", "Windows", "Heaters", "TargetID", "DepartmentID", "KadastrID")
VALUES
(101, 48, 5, 5, 1, 1, 2),
(202, 44, 4, 4, 1, 2, 2),
(122, 32, 3, 3, 2, 3, 3),
(308, 46, 4, 4, 4, 4, 3);

-- Здания
INSERT INTO public.chiefs
("Chief", "AddressChief", "Experience")
VALUES
('Иванов', 'ул.Никифорова, 56', 2),
('Петров', 'ул.Луговая, 22', 3),
('Кошкин', 'ул.Пограничная, 9', 3);

-- Имущество
INSERT INTO public.units
("UnitName", "DateStart", "Cost", "CostYear", "CostAfter", "Period", "HallID", "ChiefID")
VALUES
('Шкаф', '2005-04-27', 5600, 2020, 4700, 30, 1, 1),
('Обогреватель', '2016-06-19', 3200, 2021, 2800, 20, 2, 2),
('Компьютер', '2019-12-31', 46000, 2022, 39500, 10, 4, 3);

-- Пользователи
INSERT INTO public.users ("Login", "Password", "is_admin")
VALUES
('admin1', '9d516530dba7ae296eac0599b016c6038f230397', true),
('user1', '9d516530dba7ae296eac0599b016c6038f230397', false);
