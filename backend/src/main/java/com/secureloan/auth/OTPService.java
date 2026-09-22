package com.secureloan.auth;

import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.Map;
import java.security.SecureRandom;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OTPService {
    private final Map<String, OtpData> otpStore = new ConcurrentHashMap<>();
    private final SecureRandom random = new SecureRandom();
    public String generateOtp(String mobileNumber) {
        String otp = String.format("%06d", random.nextInt(1000000));
        otpStore.put(mobileNumber, new OtpData(otp, LocalDateTime.now().plusMinutes(5), 0));
        return otp;
    }
    public synchronized boolean verifyOtp(String mobileNumber, String otp) {
        OtpData data = otpStore.get(mobileNumber);
        if (data == null) return false;
        if (LocalDateTime.now().isAfter(data.expiry())) { otpStore.remove(mobileNumber); return false; }
        boolean valid = data.otp().equals(otp);
        if (valid || data.attempts() >= 4) otpStore.remove(mobileNumber);
        else otpStore.put(mobileNumber, new OtpData(data.otp(), data.expiry(), data.attempts() + 1));
        return valid;
    }
    private record OtpData(String otp, LocalDateTime expiry, int attempts) {}
}
