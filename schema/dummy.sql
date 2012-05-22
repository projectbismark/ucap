INSERT INTO households (id , name) VALUES ('h1','midtown');
--INSERT INTO households (id , name) VALUES ('h2','buckhead');

INSERT INTO users (id,parentdigest) VALUES ('user1',md5(get_textid('h1')));
INSERT INTO users (id,parentdigest) VALUES ('user2',md5(get_textid('h1')));
--INSERT INTO users (id,parentdigest) VALUES ('user1',md5(get_textid('h2')));
--INSERT INTO users (id,parentdigest) VALUES ('user3',md5(get_textid('h2')));

INSERT INTO devices (id,parentdigest,macid) VALUES ('device1',md5(get_textid('user1','h1')),'{aabbccddeef1,aabbccddffdd}');
INSERT INTO devices (id,parentdigest,macid) VALUES ('device2',md5(get_textid('user1','h1')),'{aabbccddeef2}');
INSERT INTO devices (id,parentdigest,macid) VALUES ('device1',md5(get_textid('user2','h1')),'{aabbccddeef3}');
INSERT INTO devices (id,parentdigest,macid) VALUES ('device3',md5(get_textid('user2','h1')),'{aabbccddeef4,aabbccddffde}');
/*INSERT INTO devices (id,parentdigest,macid) VALUES ('device1',md5(get_textid('user1','h2')),'{aabbccddeef5,aabbccddffdc}');
INSERT INTO devices (id,parentdigest,macid) VALUES ('device2',md5(get_textid('user1','h2')),'{aabbccddeef6}');
INSERT INTO devices (id,parentdigest,macid) VALUES ('device1',md5(get_textid('user3','h2')),'{aabbccddeef7}');
INSERT INTO devices (id,parentdigest,macid) VALUES ('device3',md5(get_textid('user3','h2')),'{aabbccddeef8,aabbccddffdb}');
*/
update household_caps_curr set cap = 1000 where digest = md5(get_textid('h1'));
--update household_caps_curr set cap = 2000 where digest = md5(get_textid('h2'));
update user_caps_curr set cap = 500 where digest = md5(get_textid('user1','h1'));
update user_caps_curr set cap = 300 where digest = md5(get_textid('user2','h1'));
--update user_caps_curr set cap = 900 where digest = md5(get_textid('user1','h2'));
--update user_caps_curr set cap = 1000 where digest = md5(get_textid('user3','h2'));

update device_caps_curr set cap = 300 where digest = md5(get_textid('device1','user1','h1'));
update device_caps_curr set cap = 200 where digest = md5(get_textid('device2','user1','h1'));
update device_caps_curr set cap = 100 where digest = md5(get_textid('device1','user2','h1'));
update device_caps_curr set cap = 200 where digest = md5(get_textid('device3','user2','h1'));
/*update device_caps_curr set cap = 300 where digest = md5(get_textid('device1','user1','h2'));
update device_caps_curr set cap = 300 where digest = md5(get_textid('device2','user1','h2'));
update device_caps_curr set cap = 400 where digest = md5(get_textid('device1','user3','h2'));
update device_caps_curr set cap = 800 where digest = md5(get_textid('device3','user3','h2'));*/

