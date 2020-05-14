create table Users(
	username varchar(255),
    password varchar(255),
    firstName varchar(255),
    lastName varchar(255),
    phoneNumber varchar(255),
    email varchar(255),
    role varchar(255),
	primary key(username)
);


create table Sports(
	id varchar(255),
    name varchar(255),
    coach varchar(255),
    primary key(id, name)
);

create table Equipments(
	id varchar(255),
    name varchar(255),
    primary key(id)
);

create table CheckedEquipments(
	userID varchar(255),
    equipmentID varchar(255),
    primary key(userID, equipmentID),
    foreign key(userID) references users(username),
    foreign key(equipmentID) references equipments(id)
);

create table Salary(
	coachID varchar(255),
    wage varchar(255),
    primary key(coachID),
    foreign key(coachID) references users(username)
);

create table MembershipFee(
	athleteID varchar(255),
    fee varchar(255),
    primary key(athleteID),
    foreign key(athleteID) references users(username)
);

create table Classes(
  athlete varchar(255),
  coach varchar(255),
  day varchar(255),
  time varchar(255),
  sport varchar(255),
  primary key(athlete,day,time)
);