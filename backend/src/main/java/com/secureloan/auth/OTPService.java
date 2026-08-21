package com.secureloan.auth;

import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OTPService {
    private final Map<String, OtpData> otpStore = new ConcurrentHashMap<>();
    private final Random random = new Random();
    public String generateOtp(String mobileNumber) {
        String otp = String.format("%06d", random.nextInt(1000000));
        otpStore.put(mobileNumber, new OtpData(otp, LocalDateTime.now().plusMinutes(5)));
        System.out.println("OTP for " + mobileNumber + " = " + otp);
        return otp;
    }
    public boolean verifyOtp(String mobileNumber, String otp) {
        OtpData data = otpStore.get(mobileNumber);
        if (data == null) return false;
        if (LocalDateTime.now().isAfter(data.expiry())) { otpStore.remove(mobileNumber); return false; }
        boolean valid = data.otp().equals(otp);
        if (valid) otpStore.remove(mobileNumber);
        return valid;
    }
    private record OtpData(String otp, LocalDateTime expiry) {}
}
