package com.codereview.ai.providers

import com.codereview.ai.AiClient
import com.codereview.ai.AiConfig
import com.codereview.ai.AiFinding
import com.codereview.ai.AiResponse
import com.codereview.ai.AiFindingParser
import com.codereview.ai.TestResponse
import kotlinx.serialization.json.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

internal class ClaudeClient(private val config: AiConfig) : AiClient {
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

            val request = okhttp3.Request.Builder()
                .url(config.apiUrl)
                .addHeader("x-api-key", config.apiKey)
                .addHeader("anthropic-version", "2023-06-01")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "Empty response from Claude"
            )

            if (!response.isSuccessful) {
                return AiResponse(
                    success = false,
                    findings = emptyList(),
                    errorMessage = "Claude API error: ${response.code} $responseBody"
                )
            }

            parseClaudeResponse(responseBody)
        } catch (e: Exception) {
            AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = e.message
            )
        }
    }

    private fun parseClaudeResponse(responseJson: String): AiResponse {
        val root = try {
            json.parseToJsonElement(responseJson).jsonObject
        } catch (e: Exception) {
            return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "JSON parse error: ${e.message}, input: ${responseJson.take(200)}..."
            )
        }

        val content = root["content"]?.jsonArray ?: return AiResponse(
            success = false,
            findings = emptyList(),
            errorMessage = "No content in response"
        )

        val text = content.filterIsInstance<JsonObject>()
            .firstOrNull { it["type"]?.toString() == "\"text\"" }
            ?.get("text")?.toString()?.removeSurrounding("\"") ?: return AiResponse(
            success = false,
            findings = emptyList(),
            errorMessage = "No text content in response"
        )

        val parseResult = AiFindingParser.parseFindings(text)
        return AiResponse(
            success = true,
            findings = parseResult.findings,
            expectedTotal = parseResult.expectedTotal,
            parsingDebug = parseResult.debugLog,
            rawResponse = "$responseJson\n\nExpected total: ${parseResult.expectedTotal}, Parsed: ${parseResult.findings.size}"
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

            val request = okhttp3.Request.Builder()
                .url(config.apiUrl)
                .addHeader("x-api-key", config.apiKey)
                .addHeader("anthropic-version", "2023-06-01")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "Empty response from Claude",
                    rawResponse = null
                )

            if (!response.isSuccessful) {
                // Clean up raw response by removing unnecessary whitespace
                val cleanedRawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "API error: ${response.code}",
                    rawResponse = cleanedRawResponse
                )
            }

            val root = json.parseToJsonElement(responseBody).jsonObject
            val content = root["content"]?.jsonArray
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "No content field in response",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )

            val text = content.filterIsInstance<JsonObject>()
                .firstOrNull { it["type"]?.toString() == "\"text\"" }
                ?.get("text")?.toString()
                ?.removeSurrounding("\"")
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "No text content in response",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )

            // Clean up raw response by removing unnecessary whitespace
            val cleanedRawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
            TestResponse(
                success = true,
                responseText = text,
                errorMessage = null,
                rawResponse = cleanedRawResponse
            )
        } catch (e: Exception) {
            TestResponse(
                success = false,
                responseText = "",
                errorMessage = e.message,
                rawResponse = null
            )
        }
    }
}
