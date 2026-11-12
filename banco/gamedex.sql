-- ============================================================================
-- GameDex - script do banco de dados MySQL
-- ============================================================================
--
-- O que este script faz, em ordem:
--   1. Apaga o banco "gamedex" (se existir) e cria de novo, com utf8mb4.
--   2. Cria o usuário "gamedex" (senha "Gamedex@2026"), com permissão só nesse banco.
--   3. Cria TODAS as tabelas que o Django precisa: as do catálogo e as internas do Django.
--   4. Marca todas as migrations como já aplicadas na tabela django_migrations.
--   5. Insere dados de exemplo, o admin (admin / admin123) e um usuário comum (usuario / usuario123).
--
-- Como rodar (precisa ser com o root, porque cria banco e usuário):
--   - MySQL Workbench: File > Open SQL Script, abrir este arquivo e clicar no raio (Execute).
--   - Terminal: entrar no mysql como root e rodar:  source caminho/do/projeto/banco/gamedex.sql
--
-- Como ele foi feito: rodei o "python manage.py migrate" num MySQL 8.4 limpo, gravei os dados de
-- exemplo pelo próprio Django e exportei com o mysqldump. Por isso as tabelas são exatamente as que
-- as migrations criariam. Depois só organizei e comentei. Testado no MySQL 8.4 e no MariaDB.
--
-- Funciona no MySQL 8.4 ou mais novo e no MariaDB 10.11 ou mais novo (o mínimo que o Django 6.1 aceita).
-- ============================================================================

-- ============================================================================
-- PARTE 1: o banco e o usuário do projeto
-- ============================================================================

-- SET NAMES diz pro MySQL que os textos deste arquivo estão em utf8mb4.
-- Sem isso, dependendo do terminal (principalmente no Windows), os acentos
-- dos dados de exemplo podiam ser gravados errado ("AÃ§Ã£o" em vez de "Ação").
SET NAMES utf8mb4;

-- Apaga o banco gamedex se ele já existir e cria de novo, vazio.
-- Assim dá pra rodar o script quantas vezes quiser e sempre começar do zero.
-- CUIDADO: isso apaga tudo que estiver no banco gamedex (só nele, os outros bancos não são tocados).
DROP DATABASE IF EXISTS gamedex;

-- utf8mb4 = UTF-8 completo (acentos, ç, emoji).
-- utf8mb4_unicode_ci é a "collation": a regra de comparar e ordenar textos.
-- O "ci" quer dizer case insensitive: "rpg" e "RPG" contam como iguais nas buscas.
-- Escolhi essa e não a padrão do MySQL 8 (utf8mb4_0900_ai_ci) porque ela funciona
-- tanto no MySQL quanto no MariaDB.
CREATE DATABASE gamedex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usuário próprio do projeto, com permissão SÓ no banco gamedex.
-- É ele que está no settings.py, então o projeto conecta sem ninguém precisar editar nada.
-- Crio o mesmo usuário em 3 "endereços" porque o MySQL identifica uma conexão local
-- por nomes diferentes dependendo da configuração: 'localhost', '127.0.0.1' (IPv4) ou '::1' (IPv6).
-- IF NOT EXISTS: se o usuário já existir (script rodado de novo), não dá erro.
CREATE USER IF NOT EXISTS 'gamedex'@'localhost' IDENTIFIED BY 'Gamedex@2026';
CREATE USER IF NOT EXISTS 'gamedex'@'127.0.0.1' IDENTIFIED BY 'Gamedex@2026';
CREATE USER IF NOT EXISTS 'gamedex'@'::1' IDENTIFIED BY 'Gamedex@2026';

-- O IF NOT EXISTS não muda a senha de um usuário que já existia. O ALTER USER garante
-- que a senha fica certa mesmo se alguém tiver mudado ela antes.
ALTER USER 'gamedex'@'localhost' IDENTIFIED BY 'Gamedex@2026';
ALTER USER 'gamedex'@'127.0.0.1' IDENTIFIED BY 'Gamedex@2026';
ALTER USER 'gamedex'@'::1' IDENTIFIED BY 'Gamedex@2026';

-- GRANT dá as permissões. "gamedex.*" = todas as tabelas do banco gamedex e nada mais.
-- ALL PRIVILEGES aqui inclui criar e alterar tabelas, que o "manage.py migrate" precisa
-- quando surgir uma migration nova.
GRANT ALL PRIVILEGES ON gamedex.* TO 'gamedex'@'localhost';
GRANT ALL PRIVILEGES ON gamedex.* TO 'gamedex'@'127.0.0.1';
GRANT ALL PRIVILEGES ON gamedex.* TO 'gamedex'@'::1';

-- Permissão no banco "test_gamedex", que é o banco que o "python manage.py test" cria e apaga
-- sozinho pra rodar os testes automáticos (catalogo/tests.py). Sem isso os testes dão erro de acesso.
GRANT ALL PRIVILEGES ON test_gamedex.* TO 'gamedex'@'localhost';
GRANT ALL PRIVILEGES ON test_gamedex.* TO 'gamedex'@'127.0.0.1';
GRANT ALL PRIVILEGES ON test_gamedex.* TO 'gamedex'@'::1';

-- A partir daqui, tudo é feito dentro do banco gamedex.
USE gamedex;

-- ============================================================================
-- PARTE 2: as tabelas
-- ============================================================================

-- Desliga a conferência de chave estrangeira enquanto cria as tabelas e insere os dados.
-- Sem isso a ordem importaria: não daria pra criar uma tabela que aponta pra outra que ainda não existe.
-- No final do script ela é ligada de novo.
SET FOREIGN_KEY_CHECKS = 0;

-- ---------- Tabelas internas do Django ----------

-- Lista das migrations já aplicadas. É a tabela mais importante pra compatibilidade:
-- o "manage.py migrate" consulta ela e só roda as migrations que NÃO estão aqui.
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Um registro pra cada model do projeto (inclusive os do Django).
-- O admin e as permissões usam essa tabela pra saber de qual model estão falando.
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Permissões de cada model (adicionar, alterar, apagar, ver). O Django cria 4 por model.
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Grupos de usuários (o projeto não usa, mas a tabela faz parte do sistema de login).
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ligação N:N entre grupos e permissões.
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Usuários que podem entrar no /admin/. A senha fica guardada como hash, nunca como texto.
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ligação N:N entre usuários e grupos.
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ligação N:N entre usuários e permissões avulsas.
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Histórico do que foi feito pelo admin (aparece em "Ações recentes").
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessões: é aqui que o Django lembra quem está logado no admin.
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------- Tabelas do catálogo (vêm do catalogo/models.py) ----------

-- Model Desenvolvedora. O nome da tabela é sempre "nomedoapp_nomedomodel".
CREATE TABLE `catalogo_desenvolvedora` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `pais` varchar(50) NOT NULL,
  `ano_fundacao` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `catalogo_desenvolvedora_chk_1` CHECK ((`ano_fundacao` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Categoria. O UNIQUE KEY no nome vem do unique=True.
CREATE TABLE `catalogo_categoria` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `descricao` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Plataforma.
CREATE TABLE `catalogo_plataforma` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `fabricante` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Jogo. Os ForeignKey viraram as colunas desenvolvedora_id e plataforma_id,
-- com CONSTRAINT ... FOREIGN KEY. O CHECK (ano_lancamento >= 0) vem do PositiveIntegerField.
CREATE TABLE `catalogo_jogo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(100) NOT NULL,
  `descricao` longtext NOT NULL,
  `ano_lancamento` int unsigned NOT NULL,
  `preco` decimal(8,2) NOT NULL,
  `desenvolvedora_id` bigint NOT NULL,
  `plataforma_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `catalogo_jogo_desenvolvedora_id_20a8951f_fk_catalogo_` (`desenvolvedora_id`),
  KEY `catalogo_jogo_plataforma_id_cf28f484_fk_catalogo_plataforma_id` (`plataforma_id`),
  CONSTRAINT `catalogo_jogo_desenvolvedora_id_20a8951f_fk_catalogo_` FOREIGN KEY (`desenvolvedora_id`) REFERENCES `catalogo_desenvolvedora` (`id`),
  CONSTRAINT `catalogo_jogo_plataforma_id_cf28f484_fk_catalogo_plataforma_id` FOREIGN KEY (`plataforma_id`) REFERENCES `catalogo_plataforma` (`id`),
  CONSTRAINT `catalogo_jogo_chk_1` CHECK ((`ano_lancamento` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela do meio do ManyToManyField Jogo <-> Categoria. Eu não criei ela no models.py:
-- o Django cria sozinho, com o id do jogo e o id da categoria em cada linha.
CREATE TABLE `catalogo_jogo_categorias` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `jogo_id` bigint NOT NULL,
  `categoria_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `catalogo_jogo_categorias_jogo_id_categoria_id_3ad2f854_uniq` (`jogo_id`,`categoria_id`),
  KEY `catalogo_jogo_catego_categoria_id_f81c6269_fk_catalogo_` (`categoria_id`),
  CONSTRAINT `catalogo_jogo_catego_categoria_id_f81c6269_fk_catalogo_` FOREIGN KEY (`categoria_id`) REFERENCES `catalogo_categoria` (`id`),
  CONSTRAINT `catalogo_jogo_categorias_jogo_id_4528c2b6_fk_catalogo_jogo_id` FOREIGN KEY (`jogo_id`) REFERENCES `catalogo_jogo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Avaliacao. A coluna jogo_id é o ForeignKey pro Jogo e a usuario_id é o ForeignKey
-- pro usuário que fez a avaliação (auth_user). As duas são relações 1:N.
CREATE TABLE `catalogo_avaliacao` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nota` smallint unsigned NOT NULL,
  `comentario` longtext NOT NULL,
  `data` date NOT NULL,
  `jogo_id` bigint NOT NULL,
  `usuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `catalogo_avaliacao_jogo_id_d2005725_fk_catalogo_jogo_id` (`jogo_id`),
  KEY `catalogo_avaliacao_usuario_id_0a036ed4_fk_auth_user_id` (`usuario_id`),
  CONSTRAINT `catalogo_avaliacao_jogo_id_d2005725_fk_catalogo_jogo_id` FOREIGN KEY (`jogo_id`) REFERENCES `catalogo_jogo` (`id`),
  CONSTRAINT `catalogo_avaliacao_usuario_id_0a036ed4_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogo_avaliacao_chk_1` CHECK ((`nota` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Perfil: a relação 1:1 com o usuário.
-- O que faz ser 1:1 no banco é o UNIQUE KEY na coluna usuario_id: o mesmo usuário não pode
-- aparecer em dois perfis. (Num ForeignKey normal, 1:N, a coluna pode repetir.)
-- plataforma_favorita_id aceita NULL porque a plataforma favorita é opcional.
CREATE TABLE `catalogo_perfil` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bio` longtext NOT NULL,
  `plataforma_favorita_id` bigint DEFAULT NULL,
  `usuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  KEY `catalogo_perfil_plataforma_favorita__40ec32ba_fk_catalogo_` (`plataforma_favorita_id`),
  CONSTRAINT `catalogo_perfil_plataforma_favorita__40ec32ba_fk_catalogo_` FOREIGN KEY (`plataforma_favorita_id`) REFERENCES `catalogo_plataforma` (`id`),
  CONSTRAINT `catalogo_perfil_usuario_id_a3e7553f_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- PARTE 3: os dados
-- ============================================================================
-- Cada INSERT é uma linha da tabela. Os ids vão escritos de propósito, pra os ForeignKey
-- (desenvolvedora_id, jogo_id...) apontarem pros registros certos.
-- Depois do INSERT, o AUTO_INCREMENT continua do maior id, então os próximos cadastros não dão conflito.

-- Todas as migrations marcadas como aplicadas (as do Django e as 5 do catálogo).
-- Por causa destas linhas, depois do script o "manage.py migrate" diz "No migrations to apply".
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (1,'contenttypes','0001_initial','2026-10-15 17:42:07.187168');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (2,'auth','0001_initial','2026-10-15 17:42:08.015532');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (3,'admin','0001_initial','2026-10-15 17:42:08.599354');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (4,'admin','0002_logentry_remove_auto_add','2026-10-15 17:42:08.612505');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (5,'admin','0003_logentry_add_action_flag_choices','2026-10-15 17:42:08.645472');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (6,'contenttypes','0002_remove_content_type_name','2026-10-15 17:42:08.915169');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (7,'auth','0002_alter_permission_name_max_length','2026-10-15 17:42:09.073817');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (8,'auth','0003_alter_user_email_max_length','2026-10-15 17:42:09.134447');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (9,'auth','0004_alter_user_username_opts','2026-10-15 17:42:09.158212');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (10,'auth','0005_alter_user_last_login_null','2026-10-15 17:42:09.412819');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (11,'auth','0006_require_contenttypes_0002','2026-10-15 17:42:09.422910');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (12,'auth','0007_alter_validators_add_error_messages','2026-10-15 17:42:09.453144');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (13,'auth','0008_alter_user_username_max_length','2026-10-15 17:42:09.634764');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (14,'auth','0009_alter_user_last_name_max_length','2026-10-15 17:42:09.816926');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (15,'auth','0010_alter_group_name_max_length','2026-10-15 17:42:09.865309');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (16,'auth','0011_update_proxy_permissions','2026-10-15 17:42:09.892980');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (17,'auth','0012_alter_user_first_name_max_length','2026-10-15 17:42:10.050738');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (18,'catalogo','0001_initial','2026-10-15 17:42:11.524828');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (19,'catalogo','0002_alter_jogo_preco','2026-10-15 17:42:11.540040');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (20,'catalogo','0003_alter_desenvolvedora_ano_fundacao_and_more','2026-10-15 17:42:11.704442');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (21,'catalogo','0004_alter_categoria_options_alter_plataforma_options','2026-10-15 17:42:11.718283');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (22,'sessions','0001_initial','2026-10-15 17:42:11.997961');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (23,'catalogo','0005_perfil_e_usuario_na_avaliacao','2026-11-12 17:33:48.642756');

-- Os models registrados (normalmente o migrate cria isso sozinho no final).
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (1,'admin','logentry');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (2,'auth','group');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (3,'auth','permission');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (4,'auth','user');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (7,'catalogo','avaliacao');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (8,'catalogo','categoria');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (9,'catalogo','desenvolvedora');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (10,'catalogo','jogo');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (11,'catalogo','plataforma');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (12,'catalogo','perfil');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (5,'contenttypes','contenttype');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (6,'sessions','session');

-- As permissões de cada model (também criadas automaticamente pelo migrate).
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (1,'Can add log entry',1,'add_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (2,'Can change log entry',1,'change_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (3,'Can delete log entry',1,'delete_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (4,'Can view log entry',1,'view_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (5,'Can add permission',3,'add_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (6,'Can change permission',3,'change_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (7,'Can delete permission',3,'delete_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (8,'Can view permission',3,'view_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (9,'Can add group',2,'add_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (10,'Can change group',2,'change_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (11,'Can delete group',2,'delete_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (12,'Can view group',2,'view_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (13,'Can add user',4,'add_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (14,'Can change user',4,'change_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (15,'Can delete user',4,'delete_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (16,'Can view user',4,'view_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (17,'Can add content type',5,'add_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (18,'Can change content type',5,'change_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (19,'Can delete content type',5,'delete_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (20,'Can view content type',5,'view_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (21,'Can add session',6,'add_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (22,'Can change session',6,'change_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (23,'Can delete session',6,'delete_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (24,'Can view session',6,'view_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (25,'Can add categoria',8,'add_categoria');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (26,'Can change categoria',8,'change_categoria');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (27,'Can delete categoria',8,'delete_categoria');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (28,'Can view categoria',8,'view_categoria');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (29,'Can add desenvolvedora',9,'add_desenvolvedora');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (30,'Can change desenvolvedora',9,'change_desenvolvedora');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (31,'Can delete desenvolvedora',9,'delete_desenvolvedora');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (32,'Can view desenvolvedora',9,'view_desenvolvedora');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (33,'Can add plataforma',11,'add_plataforma');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (34,'Can change plataforma',11,'change_plataforma');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (35,'Can delete plataforma',11,'delete_plataforma');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (36,'Can view plataforma',11,'view_plataforma');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (37,'Can add jogo',10,'add_jogo');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (38,'Can change jogo',10,'change_jogo');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (39,'Can delete jogo',10,'delete_jogo');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (40,'Can view jogo',10,'view_jogo');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (41,'Can add avaliação',7,'add_avaliacao');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (42,'Can change avaliação',7,'change_avaliacao');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (43,'Can delete avaliação',7,'delete_avaliacao');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (44,'Can view avaliação',7,'view_avaliacao');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (45,'Can add perfil',12,'add_perfil');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (46,'Can change perfil',12,'change_perfil');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (47,'Can delete perfil',12,'delete_perfil');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (48,'Can view perfil',12,'view_perfil');

-- Superusuário "admin" com senha "admin123".
-- A senha está como hash pbkdf2_sha256, gerado pelo make_password do próprio Django.
-- Formato: algoritmo$iterações$salt$hash. Não dá pra "desfazer" o hash e descobrir a senha:
-- no login o Django gera o hash do que foi digitado e compara.
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (1,'pbkdf2_sha256$1500000$Q1hsblFvfQRv0iiRIcqEH8$O+iNCsaYzRVJdnxmTnfyEDqXSL1U/6kaifU3QxEfeuc=',NULL,1,'admin','','','',1,1,'2026-10-15 17:42:13.635902');

-- Usuário comum "usuario" com senha "usuario123" (is_staff = 0, então é o nível user do site).
-- Serve pra testar o que um usuário comum pode e não pode fazer.
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (2,'pbkdf2_sha256$1500000$nHxG6ORk8wOfdm84BTYGvD$41/xfp/QiA6ztnvkw2KIlMmVzldLxneuXATAdOKEc0E=',NULL,0,'usuario','','','',0,1,'2026-11-12 12:00:00.000000');

-- Os autores das avaliações de exemplo. Antes a avaliação guardava só o nome digitado, agora ela
-- aponta pra um usuário. A senha '!' quer dizer "sem senha": ninguém consegue entrar com eles.
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (3,'!',NULL,0,'Ana','','','',0,1,'2026-11-12 12:00:00.000000');
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (4,'!',NULL,0,'Pedro','','','',0,1,'2026-11-12 12:00:00.000000');
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (5,'!',NULL,0,'Carla','','','',0,1,'2026-11-12 12:00:00.000000');
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (6,'!',NULL,0,'João','','','',0,1,'2026-11-12 12:00:00.000000');
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (7,'!',NULL,0,'Marina','','','',0,1,'2026-11-12 12:00:00.000000');
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (8,'!',NULL,0,'Lucas','','','',0,1,'2026-11-12 12:00:00.000000');
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (9,'!',NULL,0,'Beatriz','','','',0,1,'2026-11-12 12:00:00.000000');

-- Perfis (relação 1:1): um pro admin e um pro usuario. Os outros usuários ganham o perfil
-- sozinhos na primeira vez que abrirem "Meu perfil" (get_or_create na PerfilView).
INSERT INTO `catalogo_perfil` (`id`, `bio`, `plataforma_favorita_id`, `usuario_id`) VALUES (1,'Administrador do GameDex.',1,1);
INSERT INTO `catalogo_perfil` (`id`, `bio`, `plataforma_favorita_id`, `usuario_id`) VALUES (2,'Gosto de jogos de aventura.',3,2);

-- 5 desenvolvedoras.
INSERT INTO `catalogo_desenvolvedora` (`id`, `nome`, `pais`, `ano_fundacao`) VALUES (1,'Mojang Studios','Suécia',2009);
INSERT INTO `catalogo_desenvolvedora` (`id`, `nome`, `pais`, `ano_fundacao`) VALUES (2,'Nintendo','Japão',1889);
INSERT INTO `catalogo_desenvolvedora` (`id`, `nome`, `pais`, `ano_fundacao`) VALUES (3,'CD Projekt Red','Polônia',2002);
INSERT INTO `catalogo_desenvolvedora` (`id`, `nome`, `pais`, `ano_fundacao`) VALUES (4,'Rockstar Games','Estados Unidos',1998);
INSERT INTO `catalogo_desenvolvedora` (`id`, `nome`, `pais`, `ano_fundacao`) VALUES (5,'FromSoftware','Japão',1986);

-- 6 categorias.
INSERT INTO `catalogo_categoria` (`id`, `nome`, `descricao`) VALUES (1,'Ação','Jogos com foco em combate e reflexos rápidos.');
INSERT INTO `catalogo_categoria` (`id`, `nome`, `descricao`) VALUES (2,'Aventura','Jogos com foco em exploração e história.');
INSERT INTO `catalogo_categoria` (`id`, `nome`, `descricao`) VALUES (3,'RPG','Jogos em que o personagem evolui com experiência, itens e escolhas.');
INSERT INTO `catalogo_categoria` (`id`, `nome`, `descricao`) VALUES (4,'Mundo aberto','Jogos com um mapa grande que pode ser explorado livremente.');
INSERT INTO `catalogo_categoria` (`id`, `nome`, `descricao`) VALUES (5,'Sobrevivência','Jogos em que é preciso coletar recursos para se manter vivo.');
INSERT INTO `catalogo_categoria` (`id`, `nome`, `descricao`) VALUES (6,'Multijogador','Jogos que podem ser jogados com outras pessoas.');

-- 4 plataformas.
INSERT INTO `catalogo_plataforma` (`id`, `nome`, `fabricante`) VALUES (1,'PC','Diversos');
INSERT INTO `catalogo_plataforma` (`id`, `nome`, `fabricante`) VALUES (2,'PlayStation 5','Sony');
INSERT INTO `catalogo_plataforma` (`id`, `nome`, `fabricante`) VALUES (3,'Nintendo Switch','Nintendo');
INSERT INTO `catalogo_plataforma` (`id`, `nome`, `fabricante`) VALUES (4,'Xbox Series X|S','Microsoft');

-- 8 jogos. Preços em reais são valores de referência aproximados (preço de loja muda com o tempo).
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (1,'Minecraft','Jogo de construção e sobrevivência em um mundo feito de blocos. Dá para coletar recursos, construir e explorar sozinho ou com amigos.',2011,99.00,1,4);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (2,'The Legend of Zelda: Breath of the Wild','Link acorda depois de cem anos e precisa derrotar Calamity Ganon. O reino de Hyrule pode ser explorado em qualquer ordem.',2017,299.00,2,3);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (3,'Super Mario Odyssey','Mario viaja por vários reinos para resgatar a Princesa Peach. Com o chapéu Cappy ele consegue controlar inimigos e objetos.',2017,299.00,2,3);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (4,'Mario Kart 8 Deluxe','Jogo de corrida com personagens da Nintendo e itens para atrapalhar os adversários. Tem modo local e online.',2017,299.00,2,3);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (5,'The Witcher 3: Wild Hunt','Geralt de Rívia procura Ciri, sua filha adotiva, em um mundo de fantasia em guerra. As escolhas do jogador mudam o rumo das missões.',2015,129.99,3,1);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (6,'Cyberpunk 2077','O jogador controla V, um mercenário de Night City, uma cidade futurista dominada por corporações. A história muda conforme as escolhas feitas.',2020,199.90,3,1);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (7,'Red Dead Redemption 2','Arthur Morgan faz parte de uma gangue de foras da lei no Velho Oeste americano em 1899. Lançado em 2018 nos consoles e em 2019 no PC.',2018,249.90,4,1);
INSERT INTO `catalogo_jogo` (`id`, `titulo`, `descricao`, `ano_lancamento`, `preco`, `desenvolvedora_id`, `plataforma_id`) VALUES (8,'Elden Ring','RPG de ação nas Terras Intermédias, criado com participação de George R. R. Martin. É conhecido pela dificuldade alta.',2022,249.90,5,2);

-- Quais categorias cada jogo tem (jogo_id, categoria_id).
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (1,1,2);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (2,1,5);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (3,1,6);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (4,2,1);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (5,2,2);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (6,2,4);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (7,3,2);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (8,4,6);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (9,5,2);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (10,5,3);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (11,5,4);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (12,6,1);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (13,6,3);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (14,6,4);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (15,7,1);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (16,7,2);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (17,7,4);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (18,8,1);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (19,8,3);
INSERT INTO `catalogo_jogo_categorias` (`id`, `jogo_id`, `categoria_id`) VALUES (20,8,4);

-- Algumas avaliações de exemplo em Minecraft, The Witcher 3 e Elden Ring.
-- usuario_id aponta pros usuários Ana (3), Pedro (4), Carla (5)... criados lá em cima.
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (1,5,'Jogo há anos com meus amigos e ainda não enjoei.','2026-09-02',1,3);
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (2,4,'Muito bom, mas no começo é difícil saber o que fazer.','2026-09-20',1,4);
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (3,5,'A melhor história que já vi em um jogo.','2026-08-15',5,5);
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (4,4,'','2026-09-01',5,6);
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (5,3,'Gostei da história, mas o combate é meio travado.','2026-10-03',5,7);
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (6,5,'Difícil, mas cada chefe derrotado vale a pena.','2026-09-10',8,8);
INSERT INTO `catalogo_avaliacao` (`id`, `nota`, `comentario`, `data`, `jogo_id`, `usuario_id`) VALUES (7,2,'Desisti no segundo chefe. Difícil demais pra mim.','2026-10-05',8,9);

-- Liga de novo a conferência de chave estrangeira.
SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Banco gamedex criado com sucesso!' AS resultado;
