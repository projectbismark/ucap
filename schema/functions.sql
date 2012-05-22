CREATE OR REPLACE function 
get_textid(v1 text DEFAULT NULL, v2 text DEFAULT NULL, v3 text DEFAULT NULL, OUT id text) AS $$
	DECLARE 
		filler text;
	BEGIN 
		filler = 'xxxxxxxxxx';
		CASE 
			WHEN v1 is NULL THEN id := NULL;
			WHEN v2 is NULL THEN id := v1;
			WHEN v3 is NULL THEN id := v1 || filler || v2;
			ELSE id := v1 || filler || v2 || filler || v3;
		END CASE;
	END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE function 
maximum(v1 float, v2 float, OUT maxval float) AS $$
	BEGIN
		IF v1 >= v2 THEN
			maxval := v1;
		ELSE
			maxval = v2;
		END IF;
	END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE function 
get_parent_tables(tname text, OUT ptable text, OUT pctable text) AS $$
	BEGIN
		IF tname = 'household_caps_curr' THEN
			ptable := 'households';
			pctable := NULL;
		END IF;
		IF tname = 'device_caps_curr' THEN
			ptable := 'devices';
			pctable := 'user_caps_curr';
		END IF;
		IF tname = 'user_caps_curr' THEN
			ptable := 'users';
			pctable := 'household_caps_curr';
		END IF;
		IF tname = 'devices' THEN
			ptable := 'users';
			pctable := NULL;
		END IF;
		IF tname = 'users' THEN
			ptable := 'households';
			pctable := NULL;
		END IF;
	END;	
$$
LANGUAGE plpgsql;

CREATE OR REPLACE function 
get_child_tables(tname text, OUT ctable text, OUT cctable text) AS $$
	BEGIN
		IF tname = 'households' THEN
			ctable := 'users';
			cctable := 'household_caps_curr';
		END IF;
		IF tname = 'household_caps_curr' THEN
			ctable := 'users';
			cctable := 'user_caps_curr';
		END IF;
		IF tname = 'users' THEN
			ctable := 'devices';
			cctable := 'user_caps_curr';
		END IF;
		IF tname = 'user_caps_curr' THEN
			ctable := 'devices';
			cctable := 'device_caps_curr';
		END IF;
		IF tname = 'devices' THEN
			ctable := NULL;
			cctable := 'device_caps_curr';
		END IF;
		IF tname = 'devices_caps_curr' THEN
			ctable := NULL;
			cctable := NULL;
		END IF;
	END;	
$$
LANGUAGE plpgsql;


/*****	Function to check that mac ids in the devices table are unique.
		Iterates through the NEW mac id array and checks if any mac id matches
*****/		

CREATE OR REPLACE function check_unique_macaddr() RETURNS trigger as
$check_unique_macaddr$ 
	DECLARE
		num integer;
		st integer;
	BEGIN
		IF NEW.macid is NULL THEN
			RETURN NEW;
		END IF;
		IF TG_OP = 'INSERT' THEN
			st := 1;
		END IF;
		IF TG_OP = 'UPDATE' THEN
			st := array_upper(OLD.macid,1) + 1;
		END IF;
	
		FOR i in st..array_upper(NEW.macid,1)
		LOOP
			EXECUTE 'SELECT count(*) FROM ' 
				|| TG_TABLE_NAME
				|| ' WHERE '''
				|| NEW.macid[i]
				|| '''= ANY(macid) ;' 
			INTO num; 
			IF num > 0 THEN
				RAISE EXCEPTION 'Duplicate MAC IDs';
				RETURN NULL;
			END IF;
		END LOOP;
		RETURN NEW;
	END;
$check_unique_macaddr$
LANGUAGE plpgsql;

/*****	Function to generate digest for new entries in the household, users,
		and devices tables. For household, it returns md5 of id. For users,
		and devices, it takes the parent digest, retrieves parent id, and
		mashes it together with the its id (in front) and 10 x's in between; 
		The digest is the md5 of that. 
*****/			
CREATE OR REPLACE FUNCTION gen_digest() RETURNS trigger AS $gen_digest$
	DECLARE 
		key text;
		prec record;
		pdig text;
		hid text;
	BEGIN
		key := NEW.id;
		IF TG_TABLE_NAME != 'households' THEN
			pdig := NEW.parentdigest;
			IF TG_TABLE_NAME = 'devices' THEN
				EXECUTE 'SELECT id,parentdigest from users where digest = $1'
					INTO prec USING pdig;
				SELECT into key get_textid(NEW.id,prec.id);
				--key := NEW.id || 'xxxxxxxxxx' || prec.id;
				pdig = prec.parentdigest;
			END IF;
			EXECUTE 'SELECT id from households where digest = $1'
				INTO hid  USING pdig;
			SELECT into key get_textid(key,hid);
			--key := key || 'xxxxxxxxxx' || hid;
		END IF;
		NEW.digest := md5(key);
		RETURN NEW;
	END;
$gen_digest$
LANGUAGE plpgsql;

/*****	Function to update usage of devices. Input is the actual usage since
		the last update for a particular device. It uses the fact that only
		devices add to usage, and not users or households: the latter two only
		add to usage through devices. So it cascades up the usage tally to users
		and households by matching devices to users and users to households.
*****/
-- CHECK FOR TIMESTAMP; if currtime > enddate then move curr to history and reset
-- UPDATE device_caps_curr set usage = xyz where digest = 'asd';
CREATE OR REPLACE FUNCTION update_usage() RETURNS trigger AS $update_usage$
	DECLARE
		udigest text;
		hdigest text;
		inc_usage float;
		currtime timestamp;
	BEGIN
		IF (NEW.usage - OLD.usage < 0.1) AND (NEW.usage - OLD.usage > -0.1) THEN
		  	RETURN NEW;
		END IF;
		RAISE NOTICE 'Firing trigger %, new usage %',TG_NAME,NEW.usage ;
		IF NEW.usage < 0 THEN
			inc_usage = -1*OLD.usage;
			NEW.USAGE = 0;
		ELSE	
			inc_usage := NEW.usage;
			NEW.usage := OLD.usage + inc_usage;
		END IF;
		currtime := localtimestamp;
		--RAISE NOTICE 'time %', currtime;

		EXECUTE 'SELECT parentdigest from devices where digest = $1' 
			INTO udigest USING NEW.digest;
		EXECUTE 'SELECT parentdigest from users where digest = $1' 
			INTO hdigest USING udigest;

		RAISE NOTICE 'Pos 1';
		EXECUTE 'UPDATE user_caps_curr set usage = maximum(0,usage + $1) where digest = $2'
				USING inc_usage, udigest;
		RAISE NOTICE 'Pos 2';
		EXECUTE 'UPDATE household_caps_curr set usage = maximum(0,usage + $1) where digest = $2'
				USING inc_usage, hdigest;
		RETURN NEW;
	END;	
$update_usage$
LANGUAGE plpgsql;

/*****	Function to sanity check when updating caps on devices or users:
		Sum of caps for devices belonging to user must not exceed user's
		cap. Same for users and households.
*****/
CREATE OR REPLACE FUNCTION validate_caps_up() RETURNS trigger AS $validate_caps_up$
	DECLARE
		pdigest text;
		prec record;
		gprec record;
		drec record;
		capsum float;
		caprec record;
	BEGIN
		IF NEW.cap = OLD.cap THEN
			RETURN NEW;
		END IF;
		IF NEW.capped is FALSE THEN
			RETURN NEW;
		END IF;
		RAISE NOTICE 'Firing trigger %',TG_NAME;
		IF NEW.usage > NEW.cap THEN
			RAISE EXCEPTION 'Usage is greater than Cap.';
		END IF;
					
		SELECT INTO prec * from get_parent_tables(TG_TABLE_NAME);
		EXECUTE 'SELECT parentdigest from ' || prec.ptable ||
				' where digest = ''' || NEW.digest || ''''
			INTO pdigest;
		EXECUTE 'SELECT sum(cap) from ' || TG_TABLE_NAME || 
			' where digest in (SELECT digest from ' || prec.ptable ||
			' where parentdigest = ''' || pdigest || ''') and digest
			!= ''' || NEW.digest || ''' and capped is TRUE'
			INTO capsum; 
		IF capsum is NULL THEN
			capsum = NEW.cap;
		ELSE
			capsum := capsum + NEW.cap;
		END IF;
		EXECUTE 'SELECT cap,capped from ' || prec.pctable || 
			' where digest  = ''' || pdigest || ''''
			INTO drec;
		RAISE NOTICE 'capsum from % %',prec.ptable,capsum;	
		RAISE NOTICE 'cap, capped from % % %',prec.pctable,drec.cap,drec.capped;	
		IF TG_TABLE_NAME = 'user_caps_curr' THEN
			IF drec.capped is FALSE THEN 
				RETURN NEW;
			END IF;
			IF drec.cap >= capsum THEN
				RETURN NEW;
			ELSE
				RAISE EXCEPTION 'New cap for % greater than cap % of parent',prec.ptable,drec.cap;
				RETURN NULL;
			END IF;
			RETURN NEW;
		END IF;
		IF drec.capped is TRUE and drec.cap < capsum THEN
			RAISE EXCEPTION 'New cap for % greater than cap % of parent %',prec.ptable,drec.cap,prec.pctable;
			RETURN NULL;
		END IF;
		SELECT into gprec * from get_parent_tables(prec.pctable);
		EXECUTE 'SELECT cap,capped from ' || gprec.pctable || 
			' where digest = (SELECT parentdigest from ' || gprec.ptable ||
			' where digest = ''' || pdigest || ''')' INTO caprec;
		IF caprec.capped is FALSE or caprec.cap >= capsum THEN
			RETURN NEW;
		ELSE
			SELECT into gprec * from get_parent_tables(gprec.ptable);
			RAISE EXCEPTION 'New cap for % greater than cap for %',prec.ptable, gprec.ptable;
			RETURN NULL;
		END IF;
	END;
$validate_caps_up$
LANGUAGE plpgsql;
	
CREATE OR REPLACE FUNCTION validate_caps_down() RETURNS trigger AS $validate_caps_down$
	DECLARE
		pdigest text;
		crec record;
		gcrec record;
		capsum float;
	BEGIN
		IF NEW.capped is FALSE THEN
			RETURN NEW;
		END IF;
		IF NEW.cap > OLD.cap OR NEW.cap = OLD.cap THEN
			RETURN NEW;
		END IF;
		IF NEW.usage > NEW.cap THEN
			RAISE EXCEPTION 'Usage is greater than Cap.';
		END IF;
		RAISE NOTICE 'Firing down trigger %',TG_NAME;
		--SELECT INTO prec * from get_parent_tables(TG_TABLE_NAME);
		SELECT INTO crec * from get_child_tables(TG_TABLE_NAME);
		EXECUTE 'SELECT sum(cap) from ' || crec.cctable || 
			' where digest in (SELECT digest from ' || crec.ctable ||
			' where parentdigest = ''' || NEW.digest || ''' and capped is TRUE)'
 			INTO capsum; --USING drec;
		IF capsum > NEW.cap THEN
			RAISE EXCEPTION 'Sum of caps in % greater than new cap.',crec.ctable;
			RETURN NULL;
		END IF;
		IF TG_TABLE_NAME = 'user_caps_curr' THEN
			RETURN NEW;
		END IF;
		SELECT INTO gcrec * from get_child_tables(crec.cctable);
		EXECUTE	'SELECT sum(cap) from ' || gcrec.cctable ||
					' where capped is TRUE and digest in ' ||
					'(SELECT digest from ' || gcrec.ctable ||
				' where parentdigest in (SELECT digest from ' 
				|| crec.ctable || ' where parentdigest = ''' || NEW.digest || '''))'
 				INTO capsum; --USING drec;
		IF capsum > NEW.cap THEN
			RAISE EXCEPTION 'Sum of caps in % greater than new cap.',gcrec.ctable;
			RETURN NULL;
		END IF;
		RETURN NEW;
	END;
$validate_caps_down$
LANGUAGE plpgsql;

/*****	Function to create default user when a household is created.
*****/	
CREATE OR REPLACE FUNCTION create_default_user() RETURNS trigger AS $create_default_user$
	DECLARE
		crec record;
	BEGIN
		RAISE NOTICE 'Firing trigger %',TG_NAME;
		SELECT into crec * from get_child_tables(TG_TABLE_NAME);
		RAISE NOTICE 'INSERT into % (id,name,parentdigest) VALUES(''default'',''Default User'',''%'')',crec.ctable,NEW.digest;
		--EXECUTE 'INSERT into ' || crec.ctable || '(id,name,parentdigest)'
		--	|| ' VALUES(''default'',''Default User'',''' || NEW.digest || ''')';
		RETURN NEW;
	END;
$create_default_user$
LANGUAGE plpgsql;

/*****	Function to inherit start and end dates for the caps_curr tables.
		Currently, the start and end dates must be set for the household, and
		these values are inherited by the respective users and devices.
*****/	
CREATE OR REPLACE FUNCTION inherit_dates() RETURNS trigger AS $inherit_dates$
	DECLARE
		pdigest text;
		startdt timestamp;
		enddt timestamp;
		--ptable text;
		--pctable text;
		prec record;
	BEGIN
		IF NEW.startdt is NOT NULL AND NEW.enddt is NOT NULL THEN
			RETURN NEW;
		END IF;
		
		RAISE NOTICE 'Firing trigger %',TG_NAME;
		SELECT INTO prec * from get_parent_tables(TG_TABLE_NAME);
		IF prec.pctable is NULL THEN
			NEW.startdt := CURRENT_TIMESTAMP;
			NEW.enddt := NEW.startdt + interval '1 month';
			RETURN NEW;
		END IF;
		EXECUTE 'SELECT parentdigest from ' || prec.ptable ||
				' where digest = ''' || NEW.digest || ''''
			INTO pdigest;
		--RAISE NOTICE 'ptable % pctable % pdigest %',prec.ptable,prec.pctable,pdigest;
		EXECUTE 'SELECT startdt, enddt from ' || prec.pctable ||
				' where digest = ''' || pdigest || ''''
			INTO startdt,enddt;
		NEW.startdt := startdt;
		NEW.enddt := enddt;
		RETURN NEW;
	END;
$inherit_dates$
LANGUAGE plpgsql;

/*****	Function to add entry to caps_curr table when a unit has been created.
		Caps and usage are set to zero, and capped is set to FALSE.
*****/	
CREATE OR REPLACE FUNCTION create_caps_entry() RETURNS trigger AS $create_caps_entry$
	DECLARE 
		crec record;
	BEGIN
		RAISE NOTICE 'Firing trigger %',TG_NAME;
		SELECT INTO crec * from get_child_tables(TG_TABLE_NAME);
		EXECUTE 'INSERT into ' || crec.cctable || '(digest) '
			|| ' VALUES (''' || NEW.digest || ''')';
		RETURN NEW;
	END;
$create_caps_entry$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION notify_usage_breach() RETURNS trigger AS $notify_usage_breach$
	DECLARE 
		notifyrec record;
		prec record;
	BEGIN
		SELECT INTO prec * from get_parent_tables(TG_TABLE_NAME);
		--SELECT into notifyrec notify,notifyperc,notified from get_parent_tables(TG_TABLE_NAME);
		RAISE NOTICE 'Table %',prec.ptable;
		EXECUTE 'SELECT notify,notifyperc,notified from ' || prec.ptable into notifyrec;
		IF NEW.usage > NEW.cap AND NEW.capped is TRUE THEN
			IF TG_TABLE_NAME = 'household_caps_curr' THEN
			  NOTIFY cap_breached_disable_household;
			END IF;
			IF TG_TABLE_NAME = 'user_caps_curr' THEN
			  NOTIFY cap_breached_disable_user;
			END IF;
			IF TG_TABLE_NAME = 'device_caps_curr' THEN
			  NOTIFY cap_breached_disable_device;
			END IF;
			--RAISE NOTICE 'cap breached notification';
		END IF;
		IF notifyrec.notify is TRUE THEN
			IF NEW.usage > ((notifyrec.notifyperc/100.0) * NEW.cap) AND NEW.capped is TRUE AND notifyrec.notified is FALSE THEN
				IF TG_TABLE_NAME = 'user_caps_curr' THEN
			  		NOTIFY notify_user;
				END IF;
			END IF;
		END IF;
		IF NEW.usage < NEW.cap AND OLD.usage >= OLD.cap AND NEW.capped is TRUE THEN
			IF TG_TABLE_NAME = 'household_caps_curr' THEN
			  NOTIFY cap_updated_enable_household;
			END IF;
			IF TG_TABLE_NAME = 'user_caps_curr' THEN
			  NOTIFY cap_updated_enable_user;
			END IF;
			IF TG_TABLE_NAME = 'device_caps_curr' THEN
			  NOTIFY cap_updated_enable_device;
			END IF;
		END IF;
		IF NEW.capped is FALSE and OLD.capped is TRUE THEN
			IF TG_TABLE_NAME = 'household_caps_curr' THEN
			  NOTIFY cap_status_enable_household;
			END IF;
			IF TG_TABLE_NAME = 'user_caps_curr' THEN
			  NOTIFY cap_status_enable_user;
			END IF;
			IF TG_TABLE_NAME = 'device_caps_curr' THEN
			  NOTIFY cap_status_enable_device;
			END IF;
		END IF;
		RETURN NEW;
	END;
$notify_usage_breach$
LANGUAGE plpgsql;
