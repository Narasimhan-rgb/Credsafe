package com.secureloan.security;

import org.springframework.stereotype.Service;
import java.util.Set;

@Service
public class IpRiskService {
    private final Set<String> maliciousIps = Set.of("185.220.101.1", "45.83.64.10", "103.152.220.44", "198.51.100.66");
    public IpRiskResult analyse(String ipAddress) {
        if (ipAddress == null || ipAddress.isBlank()) return new IpRiskResult(10, false, "IP address unavailable");
        if (maliciousIps.contains(ipAddress)) return new IpRiskResult(90, true, "IP matched cyber threat intelligence");
        if (isPrivateIp(ipAddress)) return new IpRiskResult(0, false, "Internal/private network");
        return new IpRiskResult(5, false, "No known threat intelligence match");
    }
    private boolean isPrivateIp(String ip) {
        return ip.startsWith("192.168.") || ip.startsWith("10.") || ip.startsWith("127.") || ip.matches("172\\.(1[6-9]|2[0-9]|3[0-1])\\..*");
    }
    public record IpRiskResult(int score, boolean malicious, String reason) {}
}
