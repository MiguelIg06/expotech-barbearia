CREATE DATABASE IF NOT EXISTS barbearia;
USE barbearia;

-- Tabela de clientes
CREATE TABLE clientes (
    id_clientes INT AUTO_INCREMENT PRIMARY KEY,
    nome_cliente VARCHAR(100),
    telefone_cliente VARCHAR(20)
);

-- Tabela de serviços
CREATE TABLE servicos (
    id_servicos INT AUTO_INCREMENT PRIMARY KEY,
    nome_servicos VARCHAR(100),
    preco_servicos DECIMAL(10,2)
);

-- Tabela de produtos
CREATE TABLE produtos (
    id_produtos INT AUTO_INCREMENT PRIMARY KEY,
    nome_produtos VARCHAR(100),
    preco_produtos DECIMAL(10,2)
);

-- Tabela de agendamentos
CREATE TABLE agendamentos (
    id_agendamentos INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    data_hora DATETIME,
    tipo_pagamento VARCHAR(50),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id_clientes)
);

-- Tabela de relacionamento: agendamento x serviço
CREATE TABLE agendamento_servico (
    agendamento_id INT,
    servico_id INT,
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id_agendamentos),
    FOREIGN KEY (servico_id) REFERENCES servicos(id_servicos)
);

-- Tabela de relacionamento: agendamento x produto
CREATE TABLE agendamento_produto (
    agendamento_id INT,
    produto_id INT,
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id_agendamentos),
    FOREIGN KEY (produto_id) REFERENCES produtos(id_produtos)
);

-- Inserir clientes
INSERT INTO clientes (nome_cliente, telefone_cliente) VALUES
('Miguel', '1111-1111'),
('Rafaela', '2222-2222'),
('Nicolas', '3333-3333'),
('Fabrício', '4444-4444'),
('Lucas', '5555-5555'),
('Jorge', '6666-6666'),
('Matheus', '7777-7777'),
('Michele', '8888-8888'),
('Laura', '9999-9999'),
('Giovanna', '1010-1010');

-- Inserir serviços
INSERT INTO servicos (nome_servicos, preco_servicos) VALUES
('Corte Clássico', 35.00),
('Barba Modelada', 40.00),
('Bigode Estilo', 25.00),
('Corte Moderno', 45.00),
('Combo Barba e Cabelo Executivo', 85.00),
('Coloração Masculina', 70.00),
('Limpeza de Pele Masculina', 50.00),
('Design de Sobrancelhas', 20.00),
('Platinado', 200.00),
('Pezinho e Nuca', 15.00);

-- Inserir produtos
INSERT INTO produtos (nome_produtos, preco_produtos) VALUES
("Óleo de Barba Essencial", 45.00),
("Bálsamo Pós-Barba Suave", 30.00),
("Cera Modeladora Forte", 35.00),
("Shampoo 3 em 1 (Cabelo, Barba e Corpo)", 50.00),
("Gel de Barbear Transparente", 25.00),
("Tônico Capilar Fortalecedor", 60.00),
("Máscara Facial Detox Homem", 40.00),
("Condicionador de Barba Maciez Profunda", 32.00),
("Pomada Acabamento Matte", 38.00),
("Perfume Amadeirado Clássico", 85.00);

-- Inserir agendamentos
INSERT INTO agendamentos (cliente_id, data_hora, tipo_pagamento) VALUES
(1, '2025-05-26 09:00:00', 'Dinheiro'), -- Segunda-feira, 9h
(2, '2025-05-27 10:30:00', 'Cartão'),   -- Terça-feira, 10h30
(3, '2025-05-28 14:00:00', 'Pix'),      -- Quarta-feira, 14h
(4, '2025-05-29 16:15:00', 'Dinheiro'), -- Quinta-feira, 16h15
(5, '2025-05-30 11:00:00', 'Cartão'),   -- Sexta-feira, 11h
(6, '2025-06-02 08:30:00', 'Pix'),      -- Próxima Segunda-feira, 8h30
(7, '2025-06-03 19:00:00', 'Dinheiro'), -- Terça-feira, 19h
(8, '2025-06-04 12:00:00', 'Cartão'),   -- Quarta-feira, 12h
(9, '2025-06-05 20:30:00', 'Pix'),      -- Quinta-feira, 20h30
(10, '2025-06-06 15:45:00', 'Dinheiro'); -- Sexta-feira, 15h45

-- Relacionar agendamentos com serviços
INSERT INTO agendamento_servico (agendamento_id, servico_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
(6, 6), (7, 7), (8, 8), (9, 9), (10, 10);

-- Relacionar agendamentos com produtos
INSERT INTO agendamento_produto (agendamento_id, produto_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
(6, 6), (7, 7), (8, 8), (9, 9), (10, 10);


