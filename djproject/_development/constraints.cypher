CREATE CONSTRAINT user_unique IF NOT EXISTS
FOR (user:User) REQUIRE (user.id, user.graph_owner_id) IS UNIQUE;
