-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         12.2.2-MariaDB - MariaDB Server
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.14.0.7165
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para farmacia
CREATE DATABASE IF NOT EXISTS `farmacia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `farmacia`;

-- Volcando estructura para tabla farmacia.categoria
CREATE TABLE IF NOT EXISTS `categoria` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.categoria: ~4 rows (aproximadamente)
INSERT INTO `categoria` (`id_categoria`, `nombre`, `descripcion`) VALUES
	(2, 'Higiene', 'Productos personales'),
	(3, 'Vitaminas', 'Suplementos'),
	(4, 'Primeros Auxilios', 'Material médico'),
	(5, 'Genérico', 'medicamento de venta general');

-- Volcando estructura para tabla farmacia.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.cliente: ~5 rows (aproximadamente)
INSERT INTO `cliente` (`id_cliente`, `nombre`, `telefono`, `direccion`, `correo`) VALUES
	(1, 'Carlos Ramirez', '5512345678', 'Av Central', 'carlos@gmail.com'),
	(2, 'Ana Torres', '5588881111', 'Los Reyes', 'ana@gmail.com'),
	(3, 'Pedro Martinez', '5577776666', 'Chalco', 'pedro@gmail.com'),
	(4, 'Jose Hernandez', '5555555555', 'Ixtapaluca', 'jose@gmail.com'),
	(5, 'Laura Diaz', '5519191919', 'Valle', 'laura@gmail.com');

-- Volcando estructura para tabla farmacia.detalle_venta
CREATE TABLE IF NOT EXISTS `detalle_venta` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  `id_venta` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_venta` (`id_venta`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_venta`) REFERENCES `venta` (`id_venta`),
  CONSTRAINT `2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.detalle_venta: ~5 rows (aproximadamente)
INSERT INTO `detalle_venta` (`id_detalle`, `cantidad`, `precio_unitario`, `subtotal`, `id_venta`, `id_producto`) VALUES
	(2, 50, 50.00, 2500.00, 1, 2),
	(3, 20, 50.00, 1000.00, 7, 2),
	(4, 1, 50.00, 50.00, 8, 2),
	(5, 1, 50.00, 50.00, 9, 2),
	(6, 1, 50.00, 50.00, 10, 2);

-- Volcando estructura para tabla farmacia.factura
CREATE TABLE IF NOT EXISTS `factura` (
  `id_factura` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_emision` date DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `id_venta` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_factura`),
  KEY `id_venta` (`id_venta`),
  CONSTRAINT `1` FOREIGN KEY (`id_venta`) REFERENCES `venta` (`id_venta`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.factura: ~7 rows (aproximadamente)
INSERT INTO `factura` (`id_factura`, `fecha_emision`, `total`, `id_venta`) VALUES
	(1, '2026-05-01', 320.00, 1),
	(2, '2026-05-03', 760.00, 3),
	(3, '2026-05-05', 950.00, 5),
	(4, '2026-07-12', 1000.00, 7),
	(5, '2026-07-13', 50.00, 8),
	(6, '2026-07-13', 50.00, 9),
	(7, '2026-07-13', 50.00, 10);

-- Volcando estructura para tabla farmacia.fallecido
CREATE TABLE IF NOT EXISTS `fallecido` (
  `id_fallecido` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `fecha_fallecimiento` date NOT NULL,
  `causa_fallecimiento` varchar(150) NOT NULL,
  `observaciones` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_fallecido`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.fallecido: ~3 rows (aproximadamente)
INSERT INTO `fallecido` (`id_fallecido`, `nombre`, `fecha_fallecimiento`, `causa_fallecimiento`, `observaciones`) VALUES
	(1, 'Roberto Sanchez', '2025-03-15', 'Infarto', 'Cliente frecuente'),
	(2, 'Elena Morales', '2024-11-08', 'Enfermedad respiratoria', 'Registro histórico'),
	(3, 'Ricardo Flores', '2025-07-22', 'Accidente', 'Sin observaciones');

-- Volcando estructura para tabla farmacia.operaciones_procesadas
CREATE TABLE IF NOT EXISTS `operaciones_procesadas` (
  `operacion_id` char(36) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `id_venta` int(11) DEFAULT NULL,
  `id_factura` int(11) DEFAULT NULL,
  `fecha_procesamiento` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`operacion_id`),
  KEY `idx_operacion_tipo` (`tipo`),
  KEY `idx_operacion_fecha` (`fecha_procesamiento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.operaciones_procesadas: ~3 rows (aproximadamente)
INSERT INTO `operaciones_procesadas` (`operacion_id`, `tipo`, `id_venta`, `id_factura`, `fecha_procesamiento`) VALUES
	('352a1cd0-5f88-4004-9e29-efc348da6b02', 'REGISTRAR_VENTA', 10, 7, '2026-07-13 15:04:33'),
	('aedb6795-a19c-4265-a9f4-f01c4559fc00', 'REGISTRAR_VENTA', 9, 6, '2026-07-13 15:04:03'),
	('d3c984b2-2229-4cc3-b067-dc75c6abecee', 'REGISTRAR_VENTA', 8, 5, '2026-07-13 14:08:18');

-- Volcando estructura para tabla farmacia.producto
CREATE TABLE IF NOT EXISTS `producto` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `fecha_caducidad` date DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_proveedor` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `id_categoria` (`id_categoria`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  CONSTRAINT `2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.producto: ~1 rows (aproximadamente)
INSERT INTO `producto` (`id_producto`, `nombre`, `descripcion`, `precio`, `stock`, `fecha_caducidad`, `id_categoria`, `id_proveedor`) VALUES
	(2, 'Paracetamol', 'desinflamatorio general', 50.00, 27, '2027-10-16', 2, 2);

-- Volcando estructura para tabla farmacia.proveedor
CREATE TABLE IF NOT EXISTS `proveedor` (
  `id_proveedor` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.proveedor: ~3 rows (aproximadamente)
INSERT INTO `proveedor` (`id_proveedor`, `nombre`, `telefono`, `direccion`, `correo`) VALUES
	(1, 'Farmadis', '5511111111', 'CDMX', 'farmadis@gmail.com'),
	(2, 'Medicorp', '5522222222', 'CDMX', 'medicorp@gmail.com'),
	(3, 'Salud Plus', '5533333333', 'Toluca', 'saludplus@gmail.com');

-- Volcando estructura para tabla farmacia.usuario
CREATE TABLE IF NOT EXISTS `usuario` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  `apellido` varchar(50) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `contrasena` varchar(500) DEFAULT NULL,
  `rol` varchar(50) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.usuario: ~31 rows (aproximadamente)
INSERT INTO `usuario` (`id_usuario`, `nombre`, `apellido`, `correo`, `contrasena`, `rol`, `activo`) VALUES
	(1, 'Administrador', 'Sistema', 'admin@farmacia.com', 'scrypt:32768:8:1$Y82zIaCOkPe2XtHk$9c2309497a06fce1a2638f3837110939d1122d4cbe4c4ce99adb21e6e96b8043f90a7ce8f816bbcdd1544546fed8485513e9150562e7b360ec47730c451ce3e6', 'Administrador', 1),
	(2, 'María', 'García', 'empleado1@farmacia.com', 'scrypt:32768:8:1$DXq1AX1jhoub3o3S$2d4e37ed93a0d9764c9a91105ea3b395739d3388274a0e18f17a9279b1638c601dfa235dc0c08f80448b5290c1a4505458cd1ec70bd54a56d90713d0af142249', 'Empleado', 1),
	(3, 'Carlos', 'López', 'empleado2@farmacia.com', 'scrypt:32768:8:1$k5axWJfKGpOLeKcz$03ba1bcc98ba2310ac7c0c1753440871c428f9e4a72fbf05b3d0843ea1e68f9376e947f61c1bc52167080cb1c9d35940fe85f018a02bbff3212b3509a676447c', 'Empleado', 0),
	(4, 'Ana', 'Martínez', 'ana.martinez4@gmail.com', 'scrypt:32768:8:1$jZKYdawlBp8wwxds$e3338824709d50903a095627810cd23e5b5d855993326cc475e87734dc38456f13c23285c0c62eb824f7f9cd58d6947e5212827638867707decc318bdf7c574f', 'trabajador', 1),
	(5, 'Luis', 'Hernández', 'luis.hernandez5@gmail.com', 'scrypt:32768:8:1$TtUS0M83gnL0oXYi$577696cf9dc9ba1c8d3cc9555fc7cd2b636855363b4f5f9300db7f439b525732e37618f383afcf0adf6274287eb10adab01246ee8de3ccc1aa70b5998d593b39', 'trabajador', 1),
	(6, 'Sofía', 'Ramírez', 'sofia.ramirez6@gmail.com', 'scrypt:32768:8:1$uYPE3ftWpM0ZbuW4$5a48f3bc08523b61bb9fdc09fea8cfe110e6a37fb7d9e337ff04e6e3e7d785e69614c3b6c6d0bf3eed86901395bf06fb4cbd9024a140f18cb85cbca1faf0ecd0', 'trabajador', 1),
	(7, 'Diego', 'Torres', 'diego.torres7@gmail.com', 'scrypt:32768:8:1$zKDOq9U64gOjibYx$6e97b60a258983a4335d84ddcb5e557fee3a6e6f949455bc1713d5e3b1a5d745b0f3f174b2cfd6b61b27f15f8e0673199371385ac476373794a7866186bee2c8', 'trabajador', 1),
	(8, 'Valeria', 'Flores', 'valeria.flores8@gmail.com', 'scrypt:32768:8:1$DvAN2uoqAV7kiSVR$e970133de0a7938aa60626cec1b753a5a3aa0abc8b7621056ae36b0ef40e5fdfea3d9ca4052bb0b2c69bb770f9248f331d1711bedba8b7b8c41fcd054d54ebfa', 'trabajador', 1),
	(9, 'Miguel', 'Sánchez', 'miguel.sanchez9@gmail.com', 'scrypt:32768:8:1$wqws8tAZIpZi1pmF$8153e906cf75b3350c933a59d0a42cc99d4e9ba80d6f5b912e71dc4787c9e6eea2bc82ff05013c41c3d51095ea24495df80831948d7eda988c75d8164227d5f3', 'trabajador', 1),
	(10, 'Fernanda', 'Cruz', 'fernanda.cruz10@gmail.com', 'scrypt:32768:8:1$28giedGVfowMboz5$2bd5aa7279873e75d4489805635d183759b69b412bf2e8537bd3a7f978fcb9324146025e514d25ee0edd59fb339fe1176e54db5e522e744aba829dc2aac68401', 'trabajador', 1),
	(11, 'Jorge', 'Morales', 'jorge.morales11@gmail.com', 'scrypt:32768:8:1$OQAGtooLCusA04JE$d4eb3a6a0b5a6d6652f51d0db85caad586e5520f4737330c3bc223584ab61a94815f656316c7af7bd3c126ea94930cf250d7b414b9586dc5bf6724008b62a4ee', 'trabajador', 1),
	(12, 'Daniela', 'Ortiz', 'daniela.ortiz12@gmail.com', 'scrypt:32768:8:1$b2ZralNXI7FcuJkQ$036a2d33d69e7cde92044c17514b39cb9f075ef583326649479f6e37d8d0397b1763c0bf7984fec6369c5e8bae1f91e1d34d8692dab450f885dc8bc5201822c0', 'trabajador', 1),
	(13, 'Ricardo', 'Vargas', 'ricardo.vargas13@gmail.com', 'scrypt:32768:8:1$YaqEqmdW5vf5oVtX$81696cb5157ffab1208b34541b6fbfd08fa6fe5d0faab3c8d8251912b318d614e10d94b496979f263a117b3ccb5c3ae913d1e36e11154bc9d6ce8d968de5d91f', 'trabajador', 1),
	(14, 'Paola', 'Castro', 'paola.castro14@gmail.com', 'scrypt:32768:8:1$HtwFU4f0msXco7H4$94e6470bb98eed183ba0a44ed54c6bb7008505d29e695993baffb2aa9017d9a3960b8875b647a6e2273fd9b049651ec02f3fafdbc595a65ba5423096a42eba32', 'trabajador', 1),
	(15, 'Andrés', 'Rojas', 'andres.rojas15@gmail.com', 'scrypt:32768:8:1$Rpj4Pu87FuSn9NP3$73076f4b8d9227d213e7d60ce6484581bafefd7936eff82dacce974d901f1404961b62ecf54afb9d363f8205f624d0f5ee967c2e3560b77f3b73511ba32147a7', 'trabajador', 1),
	(16, 'Camila', 'Mendoza', 'camila.mendoza16@gmail.com', 'scrypt:32768:8:1$nZCbP6AKCIzbM0Ze$daae7e6e8141d7018ce795c0d31c274e4283e80fc23b67770567ad7ca5dec78a944a301a2498fdeed14d3e43cc5864e86b0c4e192c109460c5d892fe0959aeec', 'trabajador', 1),
	(17, 'Fernando', 'Silva', 'fernando.silva17@gmail.com', 'scrypt:32768:8:1$8g9TbFUdHUEGs6Zf$3e754f7e675805ba0624e6e462342f618c3c7c73eba59e86be718eae36fc4e549e509ba659f617b111c86d1211c72d4097f43c3efefc89038fd932932587aba6', 'trabajador', 1),
	(18, 'Andrea', 'Navarro', 'andrea.navarro18@gmail.com', 'scrypt:32768:8:1$xGAHyiMCAFNt5Rfs$91365af46b054ebeba4d29cde52c63d4f3a5fdfad02e4a975401b8d5665c3b250e7eb279b952d6bdd79bbdc6a4cf4fdadb820a8fbf94266fb4364193c5e533e1', 'trabajador', 1),
	(19, 'José', 'Reyes', 'jose.reyes19@gmail.com', 'scrypt:32768:8:1$xNSribi6ntf0fWi6$9eabb31441b2d09864b1e341310072543d12f8f93f8468a06ff94ce55bb0e14d17882c36128fb53d07de19f92ba61b5e7cda691db712b593cd43e0a59546c072', 'trabajador', 1),
	(20, 'Natalia', 'Guerrero', 'natalia.guerrero20@gmail.com', 'scrypt:32768:8:1$sjbc82wf6Uvp1CTr$331365cc412a558fbaa50f301fdbaa9986f64ae14a6830d195f21d16d3c9b29c60c2a61321c5bedae46e3806ac40932f17875e6700d28e469b59d146894d35f2', 'trabajador', 1),
	(21, 'Roberto', 'Jiménez', 'roberto.jimenez21@gmail.com', 'scrypt:32768:8:1$SE77I4xC043Wk69k$5a03d9d2eb9761af1511514a15b5a9783849a9f5d86e35cad4585b6c45121793f6ad76cc1fac4d11f23cfaa61d348daa8cd19c999802e19f123847989f87445d', 'trabajador', 1),
	(22, 'Karla', 'Ruiz', 'karla.ruiz22@gmail.com', 'scrypt:32768:8:1$Hxw9VVU6DBstuIp4$60c0838935f0d44d5c28aad2ce1ed0c0776410ad0e0a74aa1f4ee1951210d9b2ffd6742d7ebd71ff6820cb431c04591a89e72010f3b101e24c958304a151eddc', 'trabajador', 1),
	(23, 'Hugo', 'Aguilar', 'hugo.aguilar23@gmail.com', 'scrypt:32768:8:1$bd25ezkXCQsBDKwQ$2cab270ecab0e842ec00cc04611ced7f4cbefa0c8969c8966d4f71192a39e1e71d0292d467f7d0052535349500093923a5d75538212288579acdf7e9002fa5ef', 'trabajador', 1),
	(24, 'Gabriela', 'Molina', 'gabriela.molina24@gmail.com', 'scrypt:32768:8:1$LyAKTouNhgcPJuM8$b15bfcb2b7b20aa7e9c2b9d42a6d4942e11f0bcf6a094718b65bbc18fccc4ad82ab4b0bb018027ded88515819b06986dcd0a94cda9493d0b5541ba366b83dd0e', 'trabajador', 1),
	(25, 'Alejandro', 'Campos', 'alejandro.campos25@gmail.com', 'scrypt:32768:8:1$r0X3AKEUdvdremQo$235c0d894070076779dd4999d7b1c130020681d670bbbc4bb4879122be6cc8e931374f1f313791331e34bbffcbaa7bceddcfacdd2e0f44b3be3acca9a3fd8164', 'trabajador', 1),
	(26, 'Patricia', 'Delgado', 'patricia.delgado26@gmail.com', 'scrypt:32768:8:1$R2mjLtFWU33gcSKw$f4855615021e3008a3409ccf1c7168fce75b6070279a027808f9fc94d6b198f57d5d9098aea41af81bd703b4b8e1dbcaf5e1ac9f532a1ea85eb682c7b1f67464', 'trabajador', 1),
	(27, 'Eduardo', 'Salazar', 'eduardo.salazar27@gmail.com', 'scrypt:32768:8:1$LoNhpm2CmP8WiDtY$1122321055b2a389e6003d11d11ab85dda1dc729dc7173613258b4b7fadb70446234a1419cfd0e454e69b1767b4f840a9a395ee94305c48c3fbfe83c0c146cae', 'trabajador', 1),
	(28, 'Verónica', 'Pineda', 'veronica.pineda28@gmail.com', 'scrypt:32768:8:1$517eaxWOBs2YDezz$85f1f09ede47ff6fe59bb931791738ff0a8418eb671c8522be0f4fbabb2aba1391ec698fe6f07f0de94500e532fcb4897ab2c3644f07b1531ea29cc5ffd15450', 'trabajador', 1),
	(29, 'Francisco', 'Cervantes', 'francisco.cervantes29@gmail.com', 'scrypt:32768:8:1$EItk7pDWQp9ZzTGo$0649df135a56d34e5e932f97fb85a0eea3b30f49154d38768ccbe506504b6f0c93ccdd35aae178f188041a3ffa4ec8f55d5d0b95e16daca89922beaf4fe25e62', 'trabajador', 1),
	(30, 'Isabel', 'Núñez', 'isabel.nunez30@gmail.com', 'scrypt:32768:8:1$pYlhkMY6haFziSwc$718a6a03252c04bf851231ea4bb8c46432f56e7ecbbca6ebb9469b6a1b8481b4ba1cb6c88ab91eced33c6f64bfffc48dbf8c99c396b1ceb2e597ed66f0edf288', 'trabajador', 1),
	(31, 'Administrador', 'Sistema', 'admin@farmacia.com', 'scrypt:32768:8:1$Y82zIaCOkPe2XtHk$9c2309497a06fce1a2638f3837110939d1122d4cbe4c4ce99adb21e6e96b8043f90a7ce8f816bbcdd1544546fed8485513e9150562e7b360ec47730c451ce3e6', 'Administrador', 1);

-- Volcando estructura para tabla farmacia.venta
CREATE TABLE IF NOT EXISTS `venta` (
  `id_venta` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_venta`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `1` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla farmacia.venta: ~10 rows (aproximadamente)
INSERT INTO `venta` (`id_venta`, `fecha`, `total`, `id_cliente`, `id_usuario`) VALUES
	(1, '2026-05-01', 320.00, 1, 1),
	(2, '2026-05-02', 90.00, 2, 2),
	(3, '2026-05-03', 760.00, 3, 1),
	(4, '2026-05-04', 120.00, 4, 2),
	(5, '2026-05-05', 950.00, 1, 3),
	(6, '2026-07-12', 500.00, 1, 1),
	(7, '2026-07-12', 1000.00, 1, 1),
	(8, '2026-07-13', 50.00, 5, 2),
	(9, '2026-07-13', 50.00, 1, 2),
	(10, '2026-07-13', 50.00, 1, 2);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
