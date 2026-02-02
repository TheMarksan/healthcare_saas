DROP TABLE IF EXISTS `despesas_trimestrais`;
DROP TABLE IF EXISTS `metricas_operadoras`;
DROP TABLE IF EXISTS `import_logs`;
DROP TABLE IF EXISTS `import_rejects`;
DROP TABLE IF EXISTS `operadoras`;


CREATE TABLE `operadoras` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `registro_ans` varchar(10) NOT NULL,
  `cnpj` varchar(18) DEFAULT NULL,
  `razao_social` varchar(255) NOT NULL,
  `modalidade` varchar(100) DEFAULT NULL,
  `uf` varchar(2) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_registro_ans` (`registro_ans`),
  KEY `idx_cnpj` (`cnpj`),
  KEY `idx_uf` (`uf`),
  KEY `idx_uf_modalidade` (`uf`,`modalidade`),
  UNIQUE KEY `registro_ans` (`registro_ans`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `despesas_trimestrais` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `operadora_id` bigint DEFAULT NULL,
  `registro_ans` varchar(10) NOT NULL,
  `cnpj` varchar(18) DEFAULT NULL,
  `razao_social` varchar(255) NOT NULL,
  `uf` varchar(2) DEFAULT NULL,
  `modalidade` varchar(100) DEFAULT NULL,
  `ano` smallint NOT NULL,
  `trimestre` smallint NOT NULL,
  `valor_despesas` decimal(15,2) NOT NULL DEFAULT '0.00',
  `cadastro_incompleto` tinyint(1) DEFAULT '0',
  `cnpj_conflict` tinyint(1) DEFAULT '0',
  `cnpj_invalido` tinyint(1) DEFAULT '0',
  `razao_social_ausente` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_registro_ans` (`registro_ans`),
  KEY `idx_operadora_periodo` (`operadora_id`,`ano`,`trimestre`),
  KEY `idx_ano_trimestre` (`ano`,`trimestre`),
  KEY `idx_uf_ano_trimestre` (`uf`,`ano`,`trimestre`),
  KEY `idx_razao_social` (`razao_social`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `import_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `import_type` varchar(50) NOT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `total_lines` int DEFAULT '0',
  `success_count` int DEFAULT '0',
  `reject_count` int DEFAULT '0',
  `started_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `finished_at` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT 'running',
  `error_summary` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `import_rejects` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `import_type` varchar(20) NOT NULL,
  `line_number` int DEFAULT NULL,
  `raw_data` text DEFAULT NULL,
  `error_type` varchar(100) DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `field_name` varchar(100) DEFAULT NULL,
  `field_value` text DEFAULT NULL,
  `rejected_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `metricas_operadoras` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `operadora_id` bigint DEFAULT NULL,
  `registro_ans` varchar(10) DEFAULT NULL,
  `cnpj` varchar(18) DEFAULT NULL,
  `razao_social` varchar(255) NOT NULL,
  `uf` varchar(2) DEFAULT NULL,
  `modalidade` varchar(100) DEFAULT NULL,
  `ranking` int DEFAULT NULL,
  `total_despesas` decimal(15,2) NOT NULL DEFAULT '0.00',
  `media_trimestral` decimal(15,2) NOT NULL DEFAULT '0.00',
  `desvio_padrao` decimal(15,2) NOT NULL DEFAULT '0.00',
  `coeficiente_variacao` decimal(10,6) NOT NULL DEFAULT '0.00',
  `alta_variabilidade` tinyint(1) DEFAULT '0',
  `quantidade_trimestres` int NOT NULL DEFAULT '0',
  `cadastro_incompleto` tinyint(1) DEFAULT '0',
  `cnpj_conflict` tinyint(1) DEFAULT '0',
  `razao_social_ausente` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ranking` (`ranking`),
  KEY `idx_total_despesas` (`total_despesas`),
  KEY `idx_uf` (`uf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;