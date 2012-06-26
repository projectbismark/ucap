<?php

require_once ("Mail.php");

if ($_SERVER["REQUEST_METHOD"] == "POST")
{
	$to = "projectucap@googlegroups.com";
	
	$issue = $_POST["issue"];
	$name = $_POST["name"];
	$email = $_POST["email"];
	$message = $_POST["message"];
	
	$from = $email;
	$to = "ucap@projectbismark.net";
	$subject = "[uCap Site Contact] " . $issue;
	$headers = array ('From' => $from,
					  'To' => $to,
					  'Subject' => $subject);
	
	$host = "ssl://smtp.gmail.com";
	$port = "465";
	$username = "ucap.dev";
	$password = "bismark123";
	
	/* Validate the input */
	if (!validateName($name))
	{
		echo ("<p class='error-red'>Invalid name. Please enter a valid name.</p>");
		return;
	}
	
	if (!validateEmail($email))
	{
		echo ("<p class='error-red'>Invalid email address. Please enter a valid email address.</p>");
		return;	
	}
	
	if (!validateMessage($message))
	{
		echo ("<p class='error-red'>Invalid message. Please enter a valid message.</p>");
		return;	
	}
	
	/* Create header files */
	$message = $name . " wrote,\n\n" . $message . "\n\nSent from uCap Contact Us Page";
	
	/* Send email */
	//$ret = mail ($to, $subject, $message, $headers);
	$smtp = Mail::factory('smtp',
						  array ('host' => $host,
								 'port' => $port,
								 'auth' => true,
								 'username' => $username,
								 'password' => $password));
	$mail = $smtp->send($to, $headers, $message);
	
	if (PEAR::isError($mail))
	{
		//echo("<p>" . $mail->getMessage() . "</p>");
		echo ("<p class='error-red'>Unable to send an email. Please try again later.</p>");
	}
	else 
		echo ("<p>Thank you for contacting us. We will respond to your issue as soon as possible!</p>");
}

function validateName ($str)
{
	if (strlen($str) == 0)
		return false;
	return true;
}

function validateEmail ($str) 
{
	/**
	 * Based on RFC 2822
	 */
	$regex = "/^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/";
	if (preg_match ($regex, $str))
		return true;
	return false;
}

function validateMessage ($str)
{
	if (strlen($str) == 0)
		return false;
	return true;
}

?>