package com.codereview.ai.providers

import com.codereview.ai.AiClient
import com.codereview.ai.AiConfig
import com.codereview.ai.AiFinding
import com.codereview.ai.AiResponse
import com.codereview.ai.AiFindingParser
import com.codereview.ai.TestResponse
import kotlinx.serialization.json.*
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

internal class OpenRouterClient(private val config: AiConfig) : AiClient {
    private val json = Json { ignoreUnknownKeys = true }
    private val client = OkHttpClient.Builder()
        .connectTimeout(config.timeoutSeconds.toLong(), TimeUnit.SECONDS)
        .readTimeout(config.timeoutSeconds.toLong(), TimeUnit.SECONDS)
        .build()

    override suspend fun review(prompt: String, codeContent: String): AiResponse {
        return try {
            val fullPrompt = "$prompt\n\n代码内容：\n$codeContent"

            val requestBody = buildJsonObject {
                put("model", config.model)
                put("max_tokens", config.maxTokens)
                putJsonArray("messages") {
                    addJsonObject {
                        put("role", "user")
                        put("content", fullPrompt)
                    }
                }
            }

            val mediaType = "application/json".toMediaType()
            val body = requestBody.toString().toRequestBody(mediaType)

            // Use HttpUrl to properly parse the URL
            val cleanedUrl = config.apiUrl.trim()
            val debugInfo = buildString {
                appendLine("URL: '$cleanedUrl'")
                appendLine("URL length: ${cleanedUrl.length}")
                appendLine("Char codes: ${cleanedUrl.map{ it.code }.joinToString(", ")}")
            }
            val httpUrl = cleanedUrl.toHttpUrl()

            val request = okhttp3.Request.Builder()
                .url(httpUrl)
                .addHeader("Authorization", "Bearer ${config.apiKey}")
                .addHeader("HTTP-Referer", "https://code-review.local")
                .addHeader("X-Title", "Code Review")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "Empty response from OpenRouter\n$debugInfo"
            )

            if (!response.isSuccessful) {
                return AiResponse(
                    success = false,
                    findings = emptyList(),
                    errorMessage = "OpenRouter API error: ${response.code} $responseBody\n$debugInfo"
                )
            }

            parseOpenRouterResponse(responseBody)
        } catch (e: Exception) {
            val cleanedUrl = config.apiUrl.trim()
            val debugInfo = buildString {
                appendLine("${e.message}")
                appendLine("URL: '$cleanedUrl'")
                appendLine("URL length: ${cleanedUrl.length}")
                appendLine("Char codes: ${cleanedUrl.map{ it.code }.joinToString(", ")}")
            }
            AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = debugInfo
            )
        }
    }

    private fun parseOpenRouterResponse(responseJson: String): AiResponse {
        val root = try {
            json.parseToJsonElement(responseJson).jsonObject
        } catch (e: Exception) {
            return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "JSON parse error: ${e.message}, input: ${responseJson.take(200)}..."
            )
        }

        val choices = root["choices"]?.jsonArray ?: return AiResponse(
            success = false,
            findings = emptyList(),
            errorMessage = "No choices in response"
        )

        val text = choices.firstOrNull()?.jsonObject?.get("message")?.jsonObject?.get("content")?.toString()?.removeSurrounding("\"")
            ?: return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "No content in response"
            )

        val parseResult = AiFindingParser.parseFindings(text)
        // Include expected vs actual in raw response for debugging
        val debugInfo = "$responseJson\n\n[Parsed: ${parseResult.findings.size} findings, Expected: ${parseResult.expectedTotal}, Found tag: ${parseResult.foundTag}]"
        val cleanedRawResponse = debugInfo.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
        return AiResponse(
            success = true,
            findings = parseResult.findings,
            expectedTotal = parseResult.expectedTotal,
            parsingDebug = parseResult.debugLog,
            rawResponse = cleanedRawResponse
        )
    }

    override suspend fun testConnection(prompt: String): TestResponse {
        return try {
            val requestBody = buildJsonObject {
                put("model", config.model)
                put("max_tokens", config.maxTokens)
                putJsonArray("messages") {
                    addJsonObject {
                        put("role", "user")
                        put("content", prompt)
                    }
                }
            }

            val mediaType = "application/json".toMediaType()
            val body = requestBody.toString().toRequestBody(mediaType)

            // Use HttpUrl to properly parse the URL
            val cleanedUrl = config.apiUrl.trim()
            val httpUrl = cleanedUrl.toHttpUrl()

            val request = okhttp3.Request.Builder()
                .url(httpUrl)
                .addHeader("Authorization", "Bearer ${config.apiKey}")
                .addHeader("HTTP-Referer", "https://code-review.local")
                .addHeader("X-Title", "Code Review")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "Empty response from OpenRouter",
                    rawResponse = null
                )

            if (!response.isSuccessful) {
                val cleanedRawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "API error: ${response.code}",
                    rawResponse = cleanedRawResponse
                )
            }

            val root = try {
                json.parseToJsonElement(responseBody).jsonObject
            } catch (e: Exception) {
                return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "JSON parse error: ${e.message}",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )
            }

            val choices = root["choices"]?.jsonArray
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "No choices in response",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )

            val text = choices.firstOrNull()?.jsonObject?.get("message")?.jsonObject?.get("content")?.toString()
                ?.removeSurrounding("\"")
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "No content in response",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )

            val cleanedRawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
            TestResponse(
                success = true,
                responseText = text,
                errorMessage = null,
                rawResponse = cleanedRawResponse
            )
        } catch (e: Exception) {
            val cleanedUrl = config.apiUrl.trim()
            val debugInfo = buildString {
                appendLine("${e.message}")
                appendLine("URL: '$cleanedUrl'")
                appendLine("URL length: ${cleanedUrl.length}")
                appendLine("Char codes: ${cleanedUrl.map{ it.code }.joinToString(", ")}")
            }
            TestResponse(
                success = false,
                responseText = "",
                errorMessage = debugInfo,
                rawResponse = null
            )
        }
    }
}
