-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.40 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.9.0.6999
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for onehealthportal
CREATE DATABASE IF NOT EXISTS `onehealthportal` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `onehealthportal`;

-- Dumping structure for table onehealthportal.appointments
CREATE TABLE IF NOT EXISTS `appointments` (
  `appointment_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `hospital_id` int NOT NULL,
  `appointment_date` datetime NOT NULL,
  `appointment_time` time NOT NULL,
  `status` enum('Pending','Completed','Cancelled') DEFAULT 'Pending',
  `note` text,
  `appointment_number` varchar(20) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`appointment_id`),
  UNIQUE KEY `appointment_number` (`appointment_number`),
  KEY `user_id` (`user_id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `hospital_id` (`hospital_id`),
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  CONSTRAINT `appointments_ibfk_3` FOREIGN KEY (`hospital_id`) REFERENCES `hospitals` (`hospital_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.appointments: ~26 rows (approximately)
INSERT INTO `appointments` (`appointment_id`, `user_id`, `doctor_id`, `hospital_id`, `appointment_date`, `appointment_time`, `status`, `note`, `appointment_number`, `created_at`, `updated_at`) VALUES
	(1, 1, 1, 1, '2025-01-15 10:00:00', '10:30:00', 'Pending', 'Regular check-up', 'APPT-NO-1', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(2, 2, 2, 2, '2025-01-16 09:00:00', '09:30:00', 'Completed', 'Neurological consultation', 'APPT-NO-2', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(3, 3, 3, 3, '2025-02-01 11:00:00', '11:30:00', 'Pending', 'Skin check-up', 'APPT-NO-3', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(4, 4, 4, 4, '2025-02-02 10:00:00', '10:30:00', 'Pending', 'Child vaccination', 'APPT-NO-4', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(5, 5, 5, 5, '2025-02-03 09:00:00', '09:30:00', 'Pending', 'Knee pain consultation', 'APPT-NO-5', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(6, 6, 6, 6, '2025-02-04 08:00:00', '08:30:00', 'Pending', 'Cancer treatment follow-up', 'APPT-NO-6', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(7, 7, 7, 7, '2025-02-05 14:00:00', '14:30:00', 'Pending', 'Psychiatric evaluation', 'APPT-NO-7', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(8, 8, 8, 8, '2025-02-06 15:00:00', '15:30:00', 'Pending', 'Emergency consultation', 'APPT-NO-8', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(9, 9, 9, 9, '2025-02-07 16:00:00', '16:30:00', 'Pending', 'Kidney function test', 'APPT-NO-9', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(10, 10, 10, 10, '2025-02-08 17:00:00', '17:30:00', 'Pending', 'Gynecological check-up', 'APPT-NO-10', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(11, 11, 11, 11, '2025-02-09 18:00:00', '18:30:00', 'Pending', 'Cardiac consultation', 'APPT-NO-11', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(12, 12, 12, 12, '2025-02-10 19:00:00', '19:30:00', 'Pending', 'Gastrointestinal consultation', 'APPT-NO-12', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(13, 13, 13, 13, '2025-02-11 20:00:00', '20:30:00', 'Pending', 'Dermatological consultation', 'APPT-NO-13', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(14, 14, 14, 14, '2025-02-12 21:00:00', '21:30:00', 'Pending', 'Orthopedic consultation', 'APPT-NO-14', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(15, 15, 15, 15, '2025-02-13 22:00:00', '22:30:00', 'Pending', 'Oncology consultation', 'APPT-NO-15', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(16, 16, 16, 16, '2025-02-14 23:00:00', '23:30:00', 'Pending', 'Psychiatric follow-up', 'APPT-NO-16', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(17, 17, 17, 17, '2025-02-15 08:00:00', '08:30:00', 'Pending', 'Emergency follow-up', 'APPT-NO-17', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(18, 18, 18, 18, '2025-02-16 09:00:00', '09:30:00', 'Pending', 'Nephrology consultation', 'APPT-NO-18', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(19, 19, 19, 19, '2025-02-17 10:00:00', '10:30:00', 'Pending', 'Gynecological follow-up', 'APPT-NO-19', '2025-01-15 02:11:33', '2025-01-15 02:11:33'),
	(20, 20, 20, 20, '2025-02-18 11:00:00', '11:30:00', 'Completed', 'Cardiac follow-up', 'APPT-NO-20', '2025-01-15 02:11:33', '2025-01-22 20:29:15'),
	(48, 37, 1, 1, '2025-01-23 00:00:00', '09:30:00', 'Pending', '', 'APPT-NO-37', '2025-01-22 15:53:27', '2025-01-22 15:53:27');

-- Dumping structure for table onehealthportal.doctors
CREATE TABLE IF NOT EXISTS `doctors` (
  `doctor_id` int NOT NULL AUTO_INCREMENT,
  `title` enum('Dr.','Prof.') NOT NULL,
  `name` varchar(100) NOT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `profile_picture_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`doctor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.doctors: ~42 rows (approximately)
INSERT INTO `doctors` (`doctor_id`, `title`, `name`, `specialization`, `profile_picture_url`, `created_at`, `updated_at`, `is_active`) VALUES
	(1, 'Dr.', 'Nishantha Jayasuriya', 'Cardiologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(2, 'Dr.', 'Dilrukshi Perera', 'Cardiologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(3, 'Dr.', 'Ravindra Fernando', 'Gastroenterologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(4, 'Dr.', 'Shamali Rathnayake', 'Gastroenterologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(5, 'Dr.', 'Chaminda Silva', 'Neurologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(6, 'Dr.', 'Anura Gunawardena', 'Neurologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(7, 'Dr.', 'Nirosha Wijesinghe', 'Dermatologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(8, 'Dr.', 'Roshan Bandara', 'Dermatologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(9, 'Dr.', 'Shyama Rajapaksa', 'Orthopedist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(10, 'Dr.', 'Prasanna Jayawardena', 'Orthopedist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(11, 'Dr.', 'Tharindu Dissanayake', 'Oncologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(12, 'Dr.', 'Nadeesha Herath', 'Oncologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(13, 'Dr.', 'Saman Kumara', 'Psychiatrist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(14, 'Dr.', 'Anoma Pathirana', 'Psychiatrist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(15, 'Dr.', 'Lasith Malinga', 'Emergency Medicine Physician', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(16, 'Dr.', 'Kushani Alwis', 'Emergency Medicine Physician', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(17, 'Dr.', 'Ruwantha Perera', 'Nephrologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(18, 'Dr.', 'Sanduni Rathnayake', 'Nephrologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(19, 'Dr.', 'Dinesh Karunaratne', 'Gynecologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(20, 'Dr.', 'Shanika De Silva', 'Gynecologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 1),
	(21, 'Dr.', 'Kamal Perera', 'General Practitioner', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(22, 'Dr.', 'Nimali Fernando', 'General Practitioner', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(23, 'Dr.', 'Nishantha Jayasuriya', 'Cardiologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(24, 'Dr.', 'Dilrukshi Perera', 'Cardiologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(25, 'Dr.', 'Ravindra Fernando', 'Gastroenterologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(26, 'Dr.', 'Shamali Rathnayake', 'Gastroenterologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(27, 'Dr.', 'Chaminda Silva', 'Infectious Disease Specialist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(28, 'Dr.', 'Anura Gunawardena', 'Pulmonologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(29, 'Dr.', 'Nirosha Wijesinghe', 'Dermatologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(30, 'Dr.', 'Roshan Bandara', 'Dermatologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(31, 'Dr.', 'Shyama Rajapaksa', 'Otolaryngologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(32, 'Dr.', 'Prasanna Jayawardena', 'Orthopedist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(33, 'Dr.', 'Tharindu Dissanayake', 'Orthopedist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(34, 'Dr.', 'Nadeesha Herath', 'Oncologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(35, 'Dr.', 'Saman Kumara', 'Neurologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(36, 'Dr.', 'Anoma Pathirana', 'Emergency Medicine Physician', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(37, 'Dr.', 'Lasith Malinga', 'Nephrologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(38, 'Dr.', 'Kushani Alwis', 'Gynecologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:11:59', '2025-01-21 05:11:59', 1),
	(39, 'Dr.', 'Ruwantha Perera', 'Psychiatrist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:12:00', '2025-01-21 05:12:00', 1),
	(40, 'Dr.', 'Sanduni Rathnayake', 'Urologist', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:12:00', '2025-01-21 05:12:00', 1),
	(41, 'Dr.', 'Dinesh Karunaratne', 'Endocrinologist', 'https://i.imgur.com/lHg5t6u.jpeg', '2025-01-21 05:12:00', '2025-01-21 05:12:00', 1),
	(42, 'Dr.', 'Shanika De Silva', 'Vascular Surgeon', 'https://i.imgur.com/HF1Z3J8.jpeg', '2025-01-21 05:12:00', '2025-01-21 05:12:00', 1);

-- Dumping structure for table onehealthportal.feedback
CREATE TABLE IF NOT EXISTS `feedback` (
  `feedback_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `rating` int NOT NULL,
  `comments` text,
  `appointment_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`feedback_id`),
  KEY `user_id` (`user_id`),
  KEY `appointment_id` (`appointment_id`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`appointment_id`) ON DELETE CASCADE,
  CONSTRAINT `feedback_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.feedback: ~21 rows (approximately)
INSERT INTO `feedback` (`feedback_id`, `user_id`, `rating`, `comments`, `appointment_id`, `created_at`) VALUES
	(1, 1, 5, 'Excellent service!', 1, '2025-01-21 04:22:30'),
	(2, 2, 4, 'Very professional staff.', 2, '2025-01-21 04:22:30'),
	(3, 3, 3, 'Could improve waiting times.', 3, '2025-01-21 04:22:30'),
	(4, 4, 5, 'Great experience overall.', 4, '2025-01-21 04:22:30'),
	(5, 5, 2, 'Doctor was late.', 5, '2025-01-21 04:22:30'),
	(6, 6, 5, 'Excellent service!', 6, '2025-01-21 04:22:30'),
	(7, 7, 4, 'Very professional staff.', 7, '2025-01-21 04:22:30'),
	(8, 8, 3, 'Could improve waiting times.', 8, '2025-01-21 04:22:30'),
	(9, 9, 5, 'Great experience overall.', 9, '2025-01-21 04:22:30'),
	(10, 10, 2, 'Doctor was late.', 10, '2025-01-21 04:22:30'),
	(11, 11, 5, 'Excellent service!', 11, '2025-01-21 04:22:30'),
	(12, 12, 4, 'Very professional staff.', 12, '2025-01-21 04:22:30'),
	(13, 13, 3, 'Could improve waiting times.', 13, '2025-01-21 04:22:30'),
	(14, 14, 5, 'Great experience overall.', 14, '2025-01-21 04:22:30'),
	(15, 15, 2, 'Doctor was late.', 15, '2025-01-21 04:22:30'),
	(16, 16, 5, 'Excellent service!', 16, '2025-01-21 04:22:30'),
	(17, 17, 4, 'Very professional staff.', 17, '2025-01-21 04:22:30'),
	(18, 18, 3, 'Could improve waiting times.', 18, '2025-01-21 04:22:30'),
	(19, 19, 5, 'Great experience overall.', 19, '2025-01-21 04:22:30'),
	(20, 20, 2, 'Doctor was late.', 20, '2025-01-21 04:22:30');

-- Dumping structure for table onehealthportal.hospitaldoctor
CREATE TABLE IF NOT EXISTS `hospitaldoctor` (
  `hospitalID` int NOT NULL,
  `doctorID` int NOT NULL,
  `availability_start_time` time NOT NULL,
  `availability_end_time` time NOT NULL,
  PRIMARY KEY (`hospitalID`,`doctorID`),
  KEY `doctorID` (`doctorID`),
  CONSTRAINT `hospitaldoctor_ibfk_1` FOREIGN KEY (`hospitalID`) REFERENCES `hospitals` (`hospital_id`) ON DELETE CASCADE,
  CONSTRAINT `hospitaldoctor_ibfk_2` FOREIGN KEY (`doctorID`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.hospitaldoctor: ~84 rows (approximately)
INSERT INTO `hospitaldoctor` (`hospitalID`, `doctorID`, `availability_start_time`, `availability_end_time`) VALUES
	(1, 1, '09:00:00', '17:00:00'),
	(1, 2, '09:00:00', '17:00:00'),
	(1, 35, '09:00:00', '17:00:00'),
	(1, 36, '09:00:00', '17:00:00'),
	(2, 2, '08:00:00', '16:00:00'),
	(2, 3, '08:00:00', '16:00:00'),
	(2, 4, '08:00:00', '16:00:00'),
	(2, 36, '08:00:00', '16:00:00'),
	(2, 37, '08:00:00', '16:00:00'),
	(3, 3, '10:00:00', '18:00:00'),
	(3, 5, '10:00:00', '18:00:00'),
	(3, 6, '10:00:00', '18:00:00'),
	(3, 37, '10:00:00', '18:00:00'),
	(3, 38, '10:00:00', '18:00:00'),
	(4, 4, '07:00:00', '15:00:00'),
	(4, 7, '07:00:00', '15:00:00'),
	(4, 8, '07:00:00', '15:00:00'),
	(4, 38, '07:00:00', '15:00:00'),
	(4, 39, '07:00:00', '15:00:00'),
	(5, 5, '11:00:00', '19:00:00'),
	(5, 9, '11:00:00', '19:00:00'),
	(5, 10, '11:00:00', '19:00:00'),
	(5, 39, '11:00:00', '19:00:00'),
	(5, 40, '11:00:00', '19:00:00'),
	(6, 6, '09:00:00', '17:00:00'),
	(6, 11, '09:00:00', '17:00:00'),
	(6, 12, '09:00:00', '17:00:00'),
	(6, 40, '09:00:00', '17:00:00'),
	(6, 41, '09:00:00', '17:00:00'),
	(7, 7, '08:00:00', '16:00:00'),
	(7, 13, '08:00:00', '16:00:00'),
	(7, 14, '08:00:00', '16:00:00'),
	(7, 41, '08:00:00', '16:00:00'),
	(7, 42, '08:00:00', '16:00:00'),
	(8, 8, '10:00:00', '18:00:00'),
	(8, 15, '10:00:00', '18:00:00'),
	(8, 16, '10:00:00', '18:00:00'),
	(8, 42, '10:00:00', '18:00:00'),
	(9, 9, '07:00:00', '15:00:00'),
	(9, 17, '07:00:00', '15:00:00'),
	(9, 18, '07:00:00', '15:00:00'),
	(10, 10, '11:00:00', '19:00:00'),
	(10, 19, '11:00:00', '19:00:00'),
	(10, 20, '11:00:00', '19:00:00'),
	(11, 11, '09:00:00', '17:00:00'),
	(11, 21, '09:00:00', '17:00:00'),
	(11, 22, '09:00:00', '17:00:00'),
	(12, 12, '08:00:00', '16:00:00'),
	(12, 21, '08:00:00', '16:00:00'),
	(12, 23, '08:00:00', '16:00:00'),
	(12, 24, '08:00:00', '16:00:00'),
	(13, 13, '10:00:00', '18:00:00'),
	(13, 22, '10:00:00', '18:00:00'),
	(13, 25, '10:00:00', '18:00:00'),
	(13, 26, '10:00:00', '18:00:00'),
	(14, 14, '07:00:00', '15:00:00'),
	(14, 23, '07:00:00', '15:00:00'),
	(14, 27, '07:00:00', '15:00:00'),
	(14, 28, '07:00:00', '15:00:00'),
	(15, 15, '11:00:00', '19:00:00'),
	(15, 24, '11:00:00', '19:00:00'),
	(15, 29, '11:00:00', '19:00:00'),
	(15, 30, '11:00:00', '19:00:00'),
	(16, 16, '09:00:00', '17:00:00'),
	(16, 25, '09:00:00', '17:00:00'),
	(16, 30, '09:00:00', '17:00:00'),
	(16, 31, '09:00:00', '17:00:00'),
	(17, 17, '08:00:00', '16:00:00'),
	(17, 26, '08:00:00', '16:00:00'),
	(17, 31, '08:00:00', '16:00:00'),
	(17, 32, '08:00:00', '16:00:00'),
	(18, 18, '10:00:00', '18:00:00'),
	(18, 27, '10:00:00', '18:00:00'),
	(18, 32, '10:00:00', '18:00:00'),
	(18, 33, '10:00:00', '18:00:00'),
	(19, 19, '07:00:00', '15:00:00'),
	(19, 28, '07:00:00', '15:00:00'),
	(19, 33, '07:00:00', '15:00:00'),
	(19, 34, '07:00:00', '15:00:00'),
	(20, 1, '11:00:00', '19:00:00'),
	(20, 20, '11:00:00', '19:00:00'),
	(20, 29, '11:00:00', '19:00:00'),
	(20, 34, '11:00:00', '19:00:00'),
	(20, 35, '11:00:00', '19:00:00');

-- Dumping structure for table onehealthportal.hospitals
CREATE TABLE IF NOT EXISTS `hospitals` (
  `hospital_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `address` text,
  `phone` varchar(15) DEFAULT NULL,
  `emergency_services_available` tinyint(1) DEFAULT '0',
  `logo_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`hospital_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.hospitals: ~20 rows (approximately)
INSERT INTO `hospitals` (`hospital_id`, `name`, `address`, `phone`, `emergency_services_available`, `logo_url`, `created_at`, `updated_at`) VALUES
	(1, 'Asiri Hospital', 'No 181, Kirula Road, Colombo 05', '0115432100', 1, 'https://upload.wikimedia.org/wikipedia/en/f/f6/Asiri_Hospital_Holdings_logo.png', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(2, 'Nawaloka Hospital', '23, Deshamanya H K Dharmadasa Mawatha, Colombo 02', '0115777777', 1, 'https://nawaloka.com/static/media/logo.deca1af69916ef8ed2a9.png', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(3, 'Lanka Hospitals', 'No 578, Elvitigala Mawatha, Colombo 05', '0115430000', 1, 'https://upload.wikimedia.org/wikipedia/en/d/d1/Lanka_Hospitals_logo.png', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(4, 'Durdans Hospital', '3, Alfred Place, Colombo 03', '0112140000', 1, 'https://upload.wikimedia.org/wikipedia/commons/5/57/170120_Durdans_Hospital_Logo.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(5, 'Hemas Hospital', 'No 75, Wattala, Sri Lanka', '0117555555', 1, 'https://hemashospitals.com/wp-content/uploads/2022/08/Hemas-Logos-Depts.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(6, 'Ninewells Hospital', 'No 213, Colombo Road, Gampaha', '0332270000', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(7, 'Central Hospital', 'No 114, Norris Canal Road, Colombo 10', '0112444444', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(8, 'Kandy General Hospital', 'No 1, Peradeniya Road, Kandy', '0812233444', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(9, 'Jaffna Teaching Hospital', 'No 45, Hospital Road, Jaffna', '0212222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(10, 'Matara General Hospital', 'No 12, Galle Road, Matara', '0412222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(11, 'Badulla General Hospital', 'No 34, Bandarawela Road, Badulla', '0552222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(12, 'Anuradhapura General Hospital', 'No 56, Kurunegala Road, Anuradhapura', '0252222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(13, 'Ratnapura General Hospital', 'No 78, Colombo Road, Ratnapura', '0452222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(14, 'Gampaha General Hospital', 'No 90, Negombo Road, Gampaha', '0332222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(15, 'Kurunegala General Hospital', 'No 123, Dambulla Road, Kurunegala', '0372222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(16, 'Batticaloa General Hospital', 'No 45, Trincomalee Road, Batticaloa', '0652222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(17, 'Polonnaruwa General Hospital', 'No 67, Habarana Road, Polonnaruwa', '0272222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(18, 'Trincomalee General Hospital', 'No 89, Kinniya Road, Trincomalee', '0262222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(19, 'Vavuniya General Hospital', 'No 12, Anuradhapura Road, Vavuniya', '0242222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(20, 'Ampara General Hospital', 'No 34, Kalmunai Road, Ampara', '0632222222', 1, 'https://i.imgur.com/o6MJQaU.jpeg', '2025-01-21 04:22:30', '2025-01-21 04:22:30');

-- Dumping structure for table onehealthportal.lab_tests
CREATE TABLE IF NOT EXISTS `lab_tests` (
  `lab_test_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `hospital_id` int NOT NULL,
  `test_type` varchar(100) NOT NULL,
  `test_date` date NOT NULL,
  `test_time` time NOT NULL,
  `status` enum('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
  `result` text,
  `instruction` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`lab_test_id`),
  KEY `user_id` (`user_id`),
  KEY `hospital_id` (`hospital_id`),
  CONSTRAINT `lab_tests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `lab_tests_ibfk_2` FOREIGN KEY (`hospital_id`) REFERENCES `hospitals` (`hospital_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.lab_tests: ~31 rows (approximately)
INSERT INTO `lab_tests` (`lab_test_id`, `user_id`, `hospital_id`, `test_type`, `test_date`, `test_time`, `status`, `result`, `instruction`, `created_at`, `updated_at`) VALUES
	(1, 1, 1, 'Blood Test', '2023-10-20', '09:00:00', 'Scheduled', NULL, 'Fasting required', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(2, 2, 2, 'X-Ray', '2023-10-21', '10:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(3, 3, 3, 'MRI Scan', '2023-10-22', '11:00:00', 'Cancelled', NULL, 'Remove all metal objects', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(4, 4, 4, 'Ultrasound', '2023-10-23', '12:00:00', 'Scheduled', NULL, 'Drink water before the test', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(5, 5, 5, 'ECG', '2023-10-24', '13:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(6, 6, 6, 'Blood Test', '2023-10-25', '09:00:00', 'Scheduled', NULL, 'Fasting required', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(7, 7, 7, 'X-Ray', '2023-10-26', '10:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(8, 8, 8, 'MRI Scan', '2023-10-27', '11:00:00', 'Cancelled', NULL, 'Remove all metal objects', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(9, 9, 9, 'Ultrasound', '2023-10-28', '12:00:00', 'Scheduled', NULL, 'Drink water before the test', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(10, 10, 10, 'ECG', '2023-10-29', '13:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(11, 11, 11, 'Blood Test', '2023-10-30', '09:00:00', 'Scheduled', NULL, 'Fasting required', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(12, 12, 12, 'X-Ray', '2023-10-31', '10:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(13, 13, 13, 'MRI Scan', '2023-11-01', '11:00:00', 'Cancelled', NULL, 'Remove all metal objects', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(14, 14, 14, 'Ultrasound', '2023-11-02', '12:00:00', 'Scheduled', NULL, 'Drink water before the test', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(15, 15, 15, 'ECG', '2023-11-03', '13:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(16, 16, 16, 'Blood Test', '2023-11-04', '09:00:00', 'Scheduled', NULL, 'Fasting required', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(17, 17, 17, 'X-Ray', '2023-11-05', '10:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(18, 18, 18, 'MRI Scan', '2023-11-06', '11:00:00', 'Cancelled', NULL, 'Remove all metal objects', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(19, 19, 19, 'Ultrasound', '2023-11-07', '12:00:00', 'Scheduled', NULL, 'Drink water before the test', '2025-01-21 04:22:30', '2025-01-21 04:22:30'),
	(20, 20, 20, 'ECG', '2023-11-08', '13:00:00', 'Completed', 'Normal', 'No special instructions', '2025-01-21 04:22:30', '2025-01-21 04:22:30');

-- Dumping structure for table onehealthportal.payments
CREATE TABLE IF NOT EXISTS `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `appointment_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` datetime NOT NULL,
  `payment_status` enum('Pending','Completed','Failed') DEFAULT 'Pending',
  PRIMARY KEY (`payment_id`),
  KEY `appointment_id` (`appointment_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`appointment_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.payments: ~26 rows (approximately)
INSERT INTO `payments` (`payment_id`, `appointment_id`, `amount`, `payment_date`, `payment_status`) VALUES
	(1, 1, 5000.00, '2023-10-15 10:00:00', 'Completed'),
	(2, 2, 4500.00, '2023-10-16 11:00:00', 'Completed'),
	(3, 3, 3000.00, '2023-10-17 12:00:00', 'Failed'),
	(4, 4, 6000.00, '2023-10-18 13:00:00', 'Pending'),
	(5, 5, 5500.00, '2023-10-19 14:00:00', 'Completed'),
	(6, 6, 5000.00, '2023-10-20 15:00:00', 'Completed'),
	(7, 7, 4500.00, '2023-10-21 16:00:00', 'Completed'),
	(8, 8, 3000.00, '2023-10-22 17:00:00', 'Failed'),
	(9, 9, 6000.00, '2023-10-23 18:00:00', 'Pending'),
	(10, 10, 5500.00, '2023-10-24 19:00:00', 'Completed'),
	(11, 11, 5000.00, '2023-10-25 10:00:00', 'Completed'),
	(12, 12, 4500.00, '2023-10-26 11:00:00', 'Completed'),
	(13, 13, 3000.00, '2023-10-27 12:00:00', 'Failed'),
	(14, 14, 6000.00, '2023-10-28 13:00:00', 'Pending'),
	(15, 15, 5500.00, '2023-10-29 14:00:00', 'Completed'),
	(16, 16, 5000.00, '2023-10-30 15:00:00', 'Completed'),
	(17, 17, 4500.00, '2023-10-31 16:00:00', 'Completed'),
	(18, 18, 3000.00, '2023-11-01 17:00:00', 'Failed'),
	(19, 19, 6000.00, '2023-11-02 18:00:00', 'Pending'),
	(20, 20, 5500.00, '2023-11-03 19:00:00', 'Completed'),
	(49, 48, 3000.00, '2025-01-22 15:53:25', 'Pending');

-- Dumping structure for table onehealthportal.users
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `supabase_uid` varchar(36) NOT NULL,
  `title` enum('Mr.','Mrs.','Master','Ms.') DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `emergency_contact` varchar(15) DEFAULT NULL,
  `id_type` enum('NIC','Passport') NOT NULL,
  `nic_passport` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('Patient','Admin','Staff') DEFAULT 'Patient',
  `profile_picture_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `two_factor_enabled` tinyint(1) NOT NULL DEFAULT '0',
  `two_factor_method` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `supabase_uid` (`supabase_uid`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `nic_passport` (`nic_passport`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table onehealthportal.users: ~25 rows (approximately)
INSERT INTO `users` (`user_id`, `supabase_uid`, `title`, `first_name`, `last_name`, `phone`, `emergency_contact`, `id_type`, `nic_passport`, `email`, `role`, `profile_picture_url`, `created_at`, `updated_at`, `two_factor_enabled`, `two_factor_method`) VALUES
	(1, 'uid1', 'Mr.', 'Kamal', 'Perera', '0711234567', '0779876543', 'NIC', '901234567V', 'kamal.perera@gmail.com', 'Patient', 'https://example.com/profiles/kamal_perera.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(2, 'uid2', 'Mrs.', 'Nimali', 'Fernando', '0722345678', '0778765432', 'NIC', '902345678V', 'nimali.fernando@gmail.com', 'Patient', 'https://example.com/profiles/nimali_fernando.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(3, 'uid3', 'Mr.', 'Sunil', 'Rathnayake', '0733456789', '0777654321', 'NIC', '903456789V', 'sunil.rathnayake@gmail.com', 'Patient', 'https://example.com/profiles/sunil_rathnayake.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(4, 'uid4', 'Mrs.', 'Chamari', 'Silva', '0744567890', '0776543210', 'NIC', '904567890V', 'chamari.silva@gmail.com', 'Patient', 'https://example.com/profiles/chamari_silva.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(5, 'uid5', 'Mr.', 'Asanka', 'Gunawardena', '0755678901', '0775432109', 'NIC', '905678901V', 'asanka.gunawardena@gmail.com', 'Patient', 'https://example.com/profiles/asanka_gunawardena.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(6, 'uid6', 'Mrs.', 'Dilani', 'Wijesinghe', '0766789012', '0774321098', 'NIC', '906789012V', 'dilani.wijesinghe@gmail.com', 'Patient', 'https://example.com/profiles/dilani_wijesinghe.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(7, 'uid7', 'Mr.', 'Roshan', 'Bandara', '0777890123', '0773210987', 'NIC', '907890123V', 'roshan.bandara@gmail.com', 'Patient', 'https://example.com/profiles/roshan_bandara.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(8, 'uid8', 'Mrs.', 'Shyama', 'Rajapaksa', '0788901234', '0772109876', 'NIC', '908901234V', 'shyama.rajapaksa@gmail.com', 'Patient', 'https://example.com/profiles/shyama_rajapaksa.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(9, 'uid9', 'Mr.', 'Prasanna', 'Jayawardena', '0799012345', '0771098765', 'NIC', '909012345V', 'prasanna.jayawardena@gmail.com', 'Patient', 'https://example.com/profiles/prasanna_jayawardena.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(10, 'uid10', 'Mrs.', 'Tharindu', 'Dissanayake', '0700123456', '0770987654', 'NIC', '910123456V', 'tharindu.dissanayake@gmail.com', 'Patient', 'https://example.com/profiles/tharindu_dissanayake.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(11, 'uid11', 'Mr.', 'Nuwan', 'Kumara', '0711123456', '0779876543', 'NIC', '911234567V', 'nuwan.kumara@gmail.com', 'Patient', 'https://example.com/profiles/nuwan_kumara.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(12, 'uid12', 'Mrs.', 'Sanduni', 'Perera', '0722234567', '0778765432', 'NIC', '912345678V', 'sanduni.perera@gmail.com', 'Patient', 'https://example.com/profiles/sanduni_perera.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(13, 'uid13', 'Mr.', 'Chathura', 'Fernando', '0733345678', '0777654321', 'NIC', '913456789V', 'chathura.fernando@gmail.com', 'Patient', 'https://example.com/profiles/chathura_fernando.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(14, 'uid14', 'Mrs.', 'Kushani', 'Silva', '0744456789', '0776543210', 'NIC', '914567890V', 'kushani.silva@gmail.com', 'Patient', 'https://example.com/profiles/kushani_silva.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(15, 'uid15', 'Mr.', 'Dinesh', 'Gunawardena', '0755567890', '0775432109', 'NIC', '915678901V', 'dinesh.gunawardena@gmail.com', 'Patient', 'https://example.com/profiles/dinesh_gunawardena.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(16, 'uid16', 'Mrs.', 'Anoma', 'Wijesinghe', '0766678901', '0774321098', 'NIC', '916789012V', 'anoma.wijesinghe@gmail.com', 'Patient', 'https://example.com/profiles/anoma_wijesinghe.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(17, 'uid17', 'Mr.', 'Ruwan', 'Bandara', '0777789012', '0773210987', 'NIC', '917890123V', 'ruwan.bandara@gmail.com', 'Patient', 'https://example.com/profiles/ruwan_bandara.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(18, 'uid18', 'Mrs.', 'Shanika', 'Rajapaksa', '0788890123', '0772109876', 'NIC', '918901234V', 'shanika.rajapaksa@gmail.com', 'Patient', 'https://example.com/profiles/shanika_rajapaksa.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(19, 'uid19', 'Mr.', 'Lasith', 'Jayawardena', '0799901234', '0771098765', 'NIC', '919012345V', 'lasith.jayawardena@gmail.com', 'Patient', 'https://example.com/profiles/lasith_jayawardena.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(20, 'uid20', 'Mrs.', 'Nadeesha', 'Dissanayake', '0700012345', '0770987654', 'NIC', '920123456V', 'nadeesha.dissanayake@gmail.com', 'Patient', 'https://example.com/profiles/nadeesha_dissanayake.jpg', '2025-01-21 04:22:30', '2025-01-21 04:22:30', 0, NULL),
	(37, 'f8d2f88c-3f2a-45cb-813c-d0b376c679e1', 'Mr.', 'Imanka', 'Shaminda', '0713972522', NULL, 'NIC', '20067865453', 'imankagta@gmail.com', 'Admin', 'https://res.cloudinary.com/durkari0x/image/upload/v1737561365/user_profiles/rslocmzijenc1ifgzf1s.jpg', '2025-01-22 15:15:10', '2025-01-22 15:56:05', 0, NULL),
	(38, '4d0d779f-4e02-4675-b146-b33ccb699d36', 'Mr.', 'Kaviru ', 'Mendis ', '0717810899', NULL, 'NIC', '200519400640', 'kaviru.mendis@gmail.com', 'Staff', NULL, '2025-01-22 16:54:37', '2025-01-22 16:55:07', 0, NULL),
	(39, '48278476-9e7f-4bf3-a2ba-0867446593b6', 'Mr.', 'Sharadi', 'Gajanayake', '0701239152', '07178109899', 'NIC', '200656786623', 'sharadigajanayake91@gmail.com', 'Patient', '', '2025-01-22 16:59:32', '2025-01-22 17:00:02', 0, NULL),
	(40, 'bb41f42b-1aa9-4cb4-bded-91ff74a9a7b8', 'Mr.', 'Imanka', 'Shaminda', '0713972521', NULL, 'NIC', '1234567778', 'imanka895@gmail.com', 'Staff', NULL, '2025-01-22 18:29:54', '2025-01-22 18:30:19', 0, NULL);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
