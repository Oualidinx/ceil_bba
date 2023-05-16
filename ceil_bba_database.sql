create table category
(
	id serial
		primary key,
	label varchar(100),
	price double precision,
	price_letters varchar(1500)
);

create table language
(
	id serial
		primary key,
	label varchar(100)
);

create table level
(
	id serial
		primary key,
	label varchar(100)
);

create table session
(
	id serial
		primary key,
	label varchar(50),
	start_date date,
	end_date date,
	is_active boolean,
	is_disabled boolean
);

create table course
(
	id serial
		primary key,
	label varchar(100),
	price double precision,
	is_disabled boolean,
	fk_session_id integer
		references session,
	description varchar(2500),
	on_test boolean
);

create table "user"
(
	id serial
		primary key,
	first_name varchar(100),
	last_name varchar(100),
	birthday date,
	role varchar(10),
	fk_category_id integer
		references category,
	is_deleted smallint,
	email varchar(100) not null,
	phone_number varchar(10),
	password_hash varchar(256) not null,
	birthplace varchar(100),
	is_verified boolean,
	birth_city varchar(100)
); postgres;

create table course_language
(
	id serial
		primary key,
	fk_level_id integer
		references level,
	limit_number integer,
	actual_students_number integer,
	fk_language_id integer
		references language,
	fk_course_id integer
		references course
);

create table logs_user_price
(
	id serial
		primary key,
	fk_category_id integer
		references category,
	previous_value double precision,
	last_modification timestamp,
	updated_by integer
		references "user"
);

create table note
(
	id serial
		primary key,
	student_id integer
		references "user",
	fk_level_id integer
		references level,
	fk_language_id integer
		references language,
	mark double precision
);

create table payment_receipt
(
	id serial
		primary key,
	payment_date timestamp,
	amount double precision
);

create table subscription
(
	id serial
		primary key,
	fk_student_id integer
		references "user",
	fk_course_id integer
		references course,
	is_waiting boolean,
	is_accepted integer,
	subscription_date timestamp,
	charges_paid boolean,
	fk_payment_receipt_id integer
		references payment_receipt,
	course_day varchar(15),
	course_periode varchar(10),
	note varchar(1500)
);

