package com.secureloan.security;

import com.secureloan.entity.SecurityEvent;
import com.secureloan.enums.SecurityEventType;
import com.secureloan.repository.SecurityEventRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class AccountTakeoverService {
    private final SecurityEventRepository securityEventRepository;
    private final IpRiskService ipRiskService;
    public AccountTakeoverService(SecurityEventRepository securityEventRepository, IpRiskService ipRiskService) { this.securityEventRepository = securityEventRepository; this.ipRiskService = ipRiskService; }
    public AccountTakeoverResult analyse(Long userId, String ipAddress) {
        List<SecurityEvent> events = securityEventRepository.findByUserIdAndEventTimeAfter(userId, LocalDateTime.now().minusMinutes(30));
        long loginFailures = count(events, SecurityEventType.LOGIN_FAILURE);
        long otpFailures = count(events, SecurityEventType.OTP_FAILURE);
        boolean newDevice = contains(events, SecurityEventType.NEW_DEVICE);
        boolean successfulLogin = contains(events, SecurityEventType.LOGIN_SUCCESS);
        IpRiskService.IpRiskResult ipRisk = ipRiskService.analyse(ipAddress);
        int score = 0; List<String> reasons = new ArrayList<>();
        if (loginFailures >= 5) { score += 30; reasons.add("Five or more failed login attempts"); }
        if (otpFailures >= 3) { score += 20; reasons.add("Repeated failed OTP attempts"); }
        if (newDevice) { score += 20; reasons.add("Authentication from new device"); }
        if (ipRisk.malicious()) { score += 35; reasons.add("Login originated from threat-listed IP"); }
        if ((loginFailures > 0 || otpFailures > 0) && successfulLogin) { score += 15; reasons.add("Successful authentication after repeated failures"); }
        score = Math.min(score, 100);
        return new AccountTakeoverResult(score, reasons);
    }
    private long count(List<SecurityEvent> events, SecurityEventType type) { return events.stream().filter(event -> event.getEventType() == type).count(); }
    private boolean contains(List<SecurityEvent> events, SecurityEventType type) { return events.stream().anyMatch(event -> event.getEventType() == type); }
    public record AccountTakeoverResult(int score, List<String> reasons) {}
}
