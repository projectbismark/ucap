CREATE DOMAIN id_t AS varchar(100);
CREATE DOMAIN role_t AS varchar(10);
CREATE DOMAIN contact_t AS varchar(100);
CREATE DOMAIN address_t AS varchar(500);
CREATE DOMAIN details_t AS varchar(500);
CREATE DOMAIN name_t AS varchar(100);
CREATE DOMAIN fname_t AS varchar(100);
CREATE DOMAIN fparam_t AS varchar(1000);
CREATE DOMAIN filepath_t AS varchar(500);
CREATE DOMAIN tzone_t AS integer;
CREATE DOMAIN sha1_t AS bytea;
CREATE DOMAIN md5_t AS text;

CREATE TABLE unit_tmpl (
	id id_t,
	name name_t,
	details details_t,
	notify boolean,
	notifyperc integer,
	notified boolean,
	photo filepath_t
);

CREATE TABLE households (
	LIKE unit_tmpl,
	tzone tzone_t default 0,
	address address_t,
	digest md5_t PRIMARY KEY
);
CREATE TRIGGER gen_digest BEFORE INSERT on households FOR EACH ROW EXECUTE
PROCEDURE gen_digest();
CREATE TRIGGER create_caps_entry AFTER INSERT on households FOR EACH ROW EXECUTE
PROCEDURE create_caps_entry();

CREATE TABLE users (
	LIKE unit_tmpl,
	role role_t default 'user',
	contact contact_t,
	digest md5_t PRIMARY KEY,
	parentdigest md5_t references households(digest)
);
CREATE TRIGGER gen_digest BEFORE INSERT on users FOR EACH ROW EXECUTE PROCEDURE
gen_digest();
CREATE TRIGGER create_caps_entry AFTER INSERT on users FOR EACH ROW EXECUTE
PROCEDURE create_caps_entry();

CREATE TABLE devices (
	LIKE unit_tmpl,
	macid macaddr[] not NULL,
	digest md5_t PRIMARY KEY,
	parentdigest md5_t references users(digest)
);

CREATE TRIGGER gen_digest BEFORE INSERT on devices FOR EACH ROW EXECUTE
PROCEDURE gen_digest(); 
CREATE TRIGGER check_unique_macaddr BEFORE INSERT OR UPDATE on devices FOR EACH
ROW EXECUTE PROCEDURE check_unique_macaddr();
CREATE TRIGGER create_caps_entry AFTER INSERT on devices FOR EACH ROW EXECUTE
PROCEDURE create_caps_entry();

CREATE TABLE caps_tmpl (
--	cap float default 'Infinity',
	capped boolean default FALSE,
	cap float default 'Infinity',
	--pcap float default 'Infinity',
	--ccap float default 0,
	usage float default 0,
	startdt timestamp,
	enddt timestamp
);

CREATE TABLE household_caps_curr (
	LIKE caps_tmpl INCLUDING DEFAULTS,
	CHECK (enddt >= startdt),
	CHECK (cap >= 0 and usage >= 0),
	digest md5_t references households(digest) ON DELETE CASCADE ON UPDATE CASCADE PRIMARY KEY 
);
CREATE TRIGGER inherit_dates BEFORE INSERT on household_caps_curr FOR EACH ROW EXECUTE
PROCEDURE inherit_dates(); 
CREATE TRIGGER validate_caps_down BEFORE UPDATE on household_caps_curr FOR EACH ROW
EXECUTE PROCEDURE validate_caps_down();
CREATE TRIGGER notify_usage_breach AFTER UPDATE on household_caps_curr FOR EACH ROW
EXECUTE PROCEDURE notify_usage_breach();

CREATE TABLE user_caps_curr (
	LIKE caps_tmpl INCLUDING DEFAULTS,
	CHECK (enddt >= startdt),
	CHECK (cap >= 0 and usage >= 0),
	digest md5_t references users(digest) ON DELETE CASCADE ON UPDATE CASCADE PRIMARY KEY 
);
CREATE TRIGGER inherit_dates BEFORE INSERT on user_caps_curr FOR EACH ROW EXECUTE
PROCEDURE inherit_dates(); 
CREATE TRIGGER validate_caps_down BEFORE UPDATE on user_caps_curr FOR EACH ROW
EXECUTE PROCEDURE validate_caps_down();
CREATE TRIGGER validate_caps_up BEFORE UPDATE on user_caps_curr FOR EACH ROW
EXECUTE PROCEDURE validate_caps_up();
CREATE TRIGGER notify_usage_breach AFTER UPDATE on user_caps_curr FOR EACH ROW
EXECUTE PROCEDURE notify_usage_breach();

CREATE TABLE device_caps_curr (
	LIKE caps_tmpl INCLUDING DEFAULTS,
	CHECK (enddt >= startdt),
	CHECK (cap >= 0 and usage >= 0),
	digest md5_t references devices(digest) ON DELETE CASCADE ON UPDATE CASCADE PRIMARY KEY 
);
CREATE TRIGGER inherit_dates BEFORE INSERT on device_caps_curr FOR EACH ROW EXECUTE
PROCEDURE inherit_dates(); 
CREATE TRIGGER update_usage BEFORE UPDATE on device_caps_curr FOR EACH ROW
EXECUTE PROCEDURE update_usage();
CREATE TRIGGER validate_caps_up BEFORE UPDATE on device_caps_curr FOR EACH ROW
EXECUTE PROCEDURE validate_caps_up();
CREATE TRIGGER notify_usage_breach AFTER UPDATE on device_caps_curr FOR EACH ROW
EXECUTE PROCEDURE notify_usage_breach();

CREATE TABLE function_call_log (
	caller id_t,
	name fname_t,
	parameters fparam_t,	
	calltime timestamp
);

CREATE VIEW view_mapped AS SELECT d.id as devid, dc.capped as dcapped, dc.cap dcap, dc.usage as dusage, u.id as uid, uc.capped as ucapped,uc.cap as ucap,uc.usage as uusage, h.id as hid, hc.capped as hcapped,hc.cap as hcap,hc.usage as husage from device_caps_curr as dc, devices as d, users as u, user_caps_curr as uc, household_caps_curr as hc, households as h where dc.digest = d.digest and d.parentdigest = u.digest and u.digest = uc.digest and u.parentdigest = h.digest and hc.digest = h.digest;

CREATE TABLE userpoints (
     enabled integer default 0,
     peakhourstart timestamp,
     peakhourend timestamp,
     baseline integer default 0,
     pointperbyte real default 0.0,
     totalpoint integer default 0,
     digest md5_t references households(digest) ON DELETE CASCADE ON UPDATE CASCADE PRIMARY KEY 
);
