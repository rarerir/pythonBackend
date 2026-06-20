DO $$ BEGIN
    CREATE TYPE campaign_status AS ENUM ('active', 'paused');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- кампания
CREATE TABLE IF NOT EXISTS campaign (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
	current_status  campaign_status NOT NULL DEFAULT 'paused',
    target_status   campaign_status NOT NULL DEFAULT 'paused',
    is_managed      BOOLEAN NOT NULL DEFAULT false,
    budget_limit    NUMERIC(12,2),
    spend_today     NUMERIC(12,2) NOT NULL DEFAULT 0,
    stock_days_left INTEGER,
    stock_days_min  INTEGER,
    schedule_enabled BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- автообновление даты обновления записи
CREATE EXTENSION IF NOT EXISTS moddatetime;
DO $$ BEGIN
	CREATE TRIGGER trg_campaign_updated_at
		BEFORE UPDATE ON campaign
		FOR EACH ROW
		EXECUTE FUNCTION moddatetime(updated_at);
EXCEPTION
	WHEN duplicate_object THEN null;
END $$;

-- расписание
CREATE TABLE IF NOT EXISTS campaign_schedule (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id     UUID NOT NULL REFERENCES campaign(id) ON DELETE CASCADE,
    day_of_week     SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    CHECK (start_time < end_time)
);

-- логи
CREATE TABLE IF NOT EXISTS rule_evaluation_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id     UUID NOT NULL REFERENCES campaign(id) ON DELETE CASCADE,
    triggered_rule  TEXT,
    previous_target campaign_status,
    new_target      campaign_status,
    context         JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- индексы
CREATE INDEX IF NOT EXISTS idx_schedule_campaign ON campaign_schedule(campaign_id);
CREATE INDEX IF NOT EXISTS idx_history_campaign ON rule_evaluation_log(campaign_id);

